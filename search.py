import requests
import pandas as pd

# URL of the raw CSV file on GitHub
mentors_url = 'https://raw.githubusercontent.com/Shreyag11/Website/main/Questionnaire%20for%20Python%20Project%20(Responses)%20-%20MENTOR.csv'
mentees_url = 'https://raw.githubusercontent.com/Shreyag11/Website/main/Questionnaire%20for%20Python%20Project%20(Responses)%20-%20MENTEE.csv'

# Fetch CSV data
mentors_df = pd.read_csv(mentors_url)
mentees_df = pd.read_csv(mentees_url)

# Search term (company name) provided by the mentee
search_term = "IGIDR"

# Filter mentors based on the company name
matching_mentors = mentors_df[mentors_df['Work Experience'] == search_term]['Mentor'].tolist()

# Filter mentees based on the company name
matching_mentees = mentees_df[mentees_df['Work Experience'] == search_term]['Mentee'].tolist()

# Print or use matching mentors and mentees
print("Matching mentors from HDFC:")
for mentor in matching_mentors:
    print(mentor)

print("\nMatching mentees from HDFC:")
for mentee in matching_mentees:
    print(mentee)
