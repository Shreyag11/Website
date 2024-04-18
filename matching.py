import requests
import pandas as pd

# URL of the raw CSV file on GitHub
mentors_url = 'https://raw.githubusercontent.com/Shreyag11/Website/main/Questionnaire%20for%20Python%20Project%20(Responses)%20-%20MENTOR.csv'
mentees_url = 'https://raw.githubusercontent.com/Shreyag11/Website/main/Questionnaire%20for%20Python%20Project%20(Responses)%20-%20MENTEE.csv'


#Fetch CSV data
mentors_df = pd.read_csv(mentors_url)
mentees_df = pd.read_csv(mentees_url)

# Your matching algorithm code using mentors_data and mentees_data
# ...
# Create a dictionary to map mentors' interests to their names
mentor_expertise_dict = mentors_df.set_index('Mentor')['Expertise'].to_dict()

# Create a dictionary to map mentees' interests to their names
mentee_interests_dict = mentees_df.set_index('Mentee')['Domain'].to_dict()

# Initialize matching results dictionary
matching_results = {}

# If the number of mentors is greater than or equal to the number of mentees
if len(mentors_df) >= len(mentees_df):
    mentors_assigned = set()  # Track mentors already assigned
    for mentee, mentee_interests in mentee_interests_dict.items():
        matching_results[mentee] = []
        for mentor, mentor_expertise in mentor_expertise_dict.items():
            common_interests = set(mentee_interests.split(', ')).intersection(set(mentor_expertise.split(', ')))
            if common_interests and mentor not in mentors_assigned:
                matching_results[mentee].append(mentor)
                mentors_assigned.add(mentor)
                break
        if not matching_results[mentee]:
            matching_results[mentee] = ["No matches found"]

# If the number of mentors is less than the number of mentees
else:
    mentor_index = 0
    mentor_names = list(mentor_expertise_dict.keys())  # Convert dict_keys to list
    for mentee, mentee_interests in mentee_interests_dict.items():
        matching_results[mentee] = [mentor_names[mentor_index]]
        mentor_index = (mentor_index + 1) % len(mentor_expertise_dict)

# Convert matching results dictionary to DataFrame
matching_results_df = pd.DataFrame(matching_results.items(), columns=['Mentee', 'Matching Mentor'])

# Save or display the matching results
matching_results_df.to_excel("matching_results.xlsx", index=False)  # Save to Excel
print(matching_results_df)  # Display results in Colab output



