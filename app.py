import openai
import requests
from openai import OpenAI
import os
import json
import streamlit as st


prompt_1="""
Your task is to analyze personal loan applications by comparing them with the given loan approvals and generate tailored financial advice for clients. This involves providing assessments and recommendations based solely on the provided input data, which includes Client Data, Loan Application Data, and Loan Approval Data.
Your objective is to be approved for a personal loan for the loan purpose. Where there is one approval the recommendation will look at how close the approval was to their original application or where there are two approvals, which one it considers best and/or the pro’s and con’s of each and how close it is to the clients application.



Instructions:

  - Ensure adherence to New Zealand's CCCFA, Responsible Lending Code, and Financial Advisers Act 2008.
  - Word Limit: Keep the recommendation within {} words maximum.
  - Use only the data provided in the inputs. Do not incorporate any external information or assumptions.
  - Your analysis should strictly adhere to the information presented in the given inputs.
  - That where the loan approval is more than they applied for they should think carefully before accepting the higher amount and consider if needed.
  - That a lower interest rate or lower payments are always beneficial that clients wish to pay less interest overall, but sometime cashflow is important
  - That with debt consolidation we cannot always consolidate all debts, that sometimes it doesn't make sense to consolidate debts with lower interest rates. But CHatGPT will review what is and isn’t being consolidate and calculate if the client is better off.
  - Where we are taking security that the client understand there is a risk of losing that security if repayments are not maintained
  - That the client should be comfortable wit the repayments and have reviewed their budgets carefully and not be aware of any major changes to their financial situation before taking out a personal loan.
  - The output must be presented in the specified output JSON format provided below.
  - Ensure that there is no additional text or content before or after the output outher than the json.
  - Ensure that the advice is based solely on the data provided in the client's application, without incorporating any additional, external data.
  - The language used in the advice should be clear, concise, and easily understandable, avoiding any complex financial jargon.
  - Always refer to loan options as "loan offers" and not as "portfolio."
  - Explicitly discuss the differences and implications of choosing secured versus unsecured loans.
  - Include information that interest rates range from 9.95% to 29.95%, with an average rate of 18%, and relate this to the client's credit score, noting that the average credit score in NZ is 600.
  - Use terminology like "Lender" which can include banks, finance companies, or credit unions.
  - Advise that clients can increase their payments at any time to reduce interest.
  - Explain that a single approval, especially with a higher interest rate, might reflect a cautious credit profile, potentially due to other lenders declining the application.
  - Ensure the advice does not incorrectly associate the total loan cost (including interest) as being higher than the requested loan amount. Clarify that interest is a standard addition to the requested amount.
  - Focus on the affordability of the loan repayments, emphasizing that clients should be comfortable with the payments. Avoid making assumptions about the client's expenses, living costs, or other financial commitments.
  - Aim for a more positive tone in the advice while still highlighting essential risks. Encourage clients to be mindful of their budget and borrow only what they need.



Input Data:

"""
prompt_2="""


Instructions for Assessment and Recommendation:
  Assessment:

    Compare the client's loan application data with the approval(s).
    Calculate the total cost and repayment schedule for each approval.
    Consider the loan purpose and client's stated objectives.
    Identify the best fitting loan option or highlight the pros and cons of each.

  Recommendation:

    Format: Paragraph, professional yet friendly tone, plain English.
    Content: Suggest the most suitable loan option based on the assessment.
    Considerations: Discuss any potential shortfalls or over-borrowing risks.
    Highlight the implications of interest rates and repayment terms.
    Advise on debt consolidation specifics, if applicable.
    Remind clients of security risks and the importance of comfortable repayments.

Output JSON Structure:

  {
   "assessment":"",
   "recommendation":""

  }


Output:

"""

if "text_show" not in st.session_state:
    st.session_state.text_show = ""

if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "res_len" not in st.session_state:
    st.session_state.res_len = ""

if 'selected_items' not in st.session_state:
    st.session_state['selected_items'] = []

def get_response_from_openai(prompt_in):
  try:
    # print(prompt_in)

    client = OpenAI()

    response = client.chat.completions.create(
      model="gpt-4",
      messages=[
        {
          "role": "user",
          "content": prompt_in
        }
      ],
      temperature=1,
      max_tokens=3000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    # return response.choices[0].text
    return response.choices[0].message.content
  except Exception as e:
    print(e)

def format_loan_advisory_system_info(data):
    # data = json.loads(json_data)

    output = []
    # Client Data Collection
    output.append("Client Data Collection:")
    for key, value in data['client_data_collection']['form_fields'].items():
        output.append(f"- {key}: {value}")
    output.append("")

    # Loan Application Data
    output.append("Loan Application Data:")
    for key, value in data['loan_application_data']['form_fields'].items():
        output.append(f"- {key}: {value}")
    output.append("")

    # Loan Approval Data
    output.append("Loan Approval Data:")
    for i, approval in enumerate(data['loan_approval_data']['approvals'], start=1):
        output.append(f"Approval {i}:")
        for key, value in approval.items():
            output.append(f"  - {key}: {value}")
        output.append("")

    # Joining all pieces of text with line breaks
    formatted_text = "\n".join(output)
    return formatted_text

def remove_null_or_empty_keys(in_data):
    if isinstance(in_data, dict):
        return {k: remove_null_or_empty_keys(v) for k, v in in_data.items() if v not in [None, ""]}
    elif isinstance(in_data, list):
        return [remove_null_or_empty_keys(v) for v in in_data if v not in [None, ""]]
    else:
        return in_data
    

st.title('Using AI to provide digital advice on personal loans to consumers')

api_key_openai = st.sidebar.text_input("Enter your OpenAI API key",type="password")
if api_key_openai:
    openai.api_key = api_key_openai
    os.environ['OPENAI_API_KEY'] = api_key_openai

    client = openai
    # Initialize variables
    client_data = {}
    loan_application_data = {}
    loan_approval_data = []

    # Streamlit app layout

    # Client Data Collection
    st.subheader('Client Data')
    client_data['status'] = st.selectbox('Marital Status', ["",'Single', 'Married', 'Divorced', 'Widowed'])
    client_data['credit_score'] = st.text_input('Credit Score')
    client_data['residency_status'] = st.selectbox('Residency Status', ["",'Citizen', 'Permanent Resident', 'Non-Resident'])
    client_data['housing_situation'] = st.selectbox('Housing Situation', ["",'Homeowner', 'Renting', 'Living with Family'])
    client_data['monthly_income'] = st.text_input('Monthly Income')

    # Loan Application Data
    st.subheader('Loan Application Data')
    loan_application_data['loan_amount_requested'] = st.text_input('Loan Amount Requested')
    loan_application_data['loan_term'] = st.text_input('Loan Term')
    loan_application_data['payment_frequency'] = st.selectbox('Payment Frequency', ["",'Week', 'Fortnight', 'Month', 'Year'])
    loan_application_data['loan_purpose'] = st.text_input('Loan Purpose')
    loan_application_data['additional_notes'] = st.text_area('Additional Notes')

    # Loan Approval Data
    st.subheader('Loan Approval Data')
    number_of_approvals = st.number_input('Number of Loan Approvals', min_value=1, max_value=2, value=1)

    for i in range(int(number_of_approvals)):
        st.markdown(f'### Loan Approval {i + 1}')
        loan_approval_data.append({
            'approved_loan_amount': st.text_input('Approved Loan Amount', key=f'approved_loan_amount_{i}'),
            'approved_interest_rate': st.text_input('Approved Interest Rate', key=f'approved_interest_rate_{i}'),
            'approved_loan_term': st.text_input('Approved Loan Term', key=f'approved_loan_term_{i}'),
            'approved_repayment_amount': st.text_input('Approved Repayment Amount', key=f'approved_repayment_amount_{i}'),
            'repayment_frequency': st.selectbox('Repayment Frequency', ["",'Week', 'Fortnight', 'Month', 'Year'], key=f'repayment_frequency_{i}'),
            'loan_conditions': st.text_area('Loan Conditions', key=f'loan_conditions_{i}')
        })

    if number_of_approvals == 1:
         st.session_state.res_len ="250"

    if number_of_approvals == 2:
          st.session_state.res_len ="350"
    
  
      
    # Submit button
    if st.button('Submit'):
        with st.spinner('Generating...'):
        # Compile data into the specified JSON format
          data = {
              "client_data_collection": {
                  "form_fields": client_data
              },
              "loan_application_data": {
                  "form_fields": loan_application_data
              },
              "loan_approval_data": {
                  "approvals": loan_approval_data
              }
          }
          print("--------------------------------------------------")
          data_new=remove_null_or_empty_keys(data)
          # st.json(data)
          # new_data=json(data)
          st.subheader('Assessment & Recommendation')
          print(data_new)
          print("--------------------------------------------------")
          # Run the Streamlit app (uncomment the line below to run the app directly with this script)
          # st._main_run_cl()
          formatted_text = format_loan_advisory_system_info(data_new)
          final_prompt=prompt_1.format(st.session_state.res_len)+formatted_text+prompt_2
          # st.write(final_prompt)
          out=get_response_from_openai(final_prompt)
          st.write("-----------------------------")
          try:
          # st.write(out)
            fin=json.loads(out)
            st.session_state.button_clicked = False

            st.json(fin)
          except:
            st.write(out)   

else:
   st.write("Upload Your OpenAI API Key To Proceed.")            