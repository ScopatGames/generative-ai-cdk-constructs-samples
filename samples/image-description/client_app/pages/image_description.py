#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
# Standard library imports
from io import BytesIO
import os
import base64
# Third party imports
import streamlit as st
from dotenv import load_dotenv
import boto3
from streamlit_javascript import st_javascript
# Local imports
from common.cognito_helper import CognitoHelper
from common.streamlit_utils import hide_deploy_button
from graphql.graphql_mutation_client import GraphQLMutationClient  
from graphql.graphql_subscription_client import GraphQLSubscriptionClient
from graphql.mutations import Mutations
from graphql.subscriptions import Subscriptions
from streamlit_option_menu import option_menu
from st_pages import show_pages,Section, Page, hide_pages,add_indentation
from streamlit_extras.switch_page_button import switch_page

#========================================================================================
# [Model] Load configuration and environment variables
#========================================================================================
# Load environment variables from .env file
load_dotenv() 

# Configure buckets and API endpoint  
S3_INPUT_BUCKET = os.environ.get("S3_INPUT_BUCKET")
S3_PROCESSED_BUCKET = os.environ.get("S3_PROCESSED_BUCKET")
GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT")  


# Get selected source file if authenticated

#========================================================================================
# [Controller] Networking: GraphQL mutation helper functions 
#========================================================================================
def generate_summary(source_filename):
    """Send summary job request to GraphQL API."""

    if auth.is_authenticated():

        # Get user tokens
        access_token, id_token = auth.get_user_tokens()
        
        # Decode ID token
        decoded_token = auth.decode_id_token(id_token)
        
        # Get summary job ID 
        summary_job_id = decoded_token.get("cognito:username", id_token[:10])

        # Call GraphQL mutation
        mutation_client = GraphQLMutationClient(GRAPHQL_ENDPOINT, id_token)
        
        print("======LANGUAGE==========")
        print(st.session_state["language"])

        print("======LANGUAGE==========")

        variables = {
            "summaryInput": {
                "files": [{"status": "", "name": source_filename}],
                "summary_job_id": summary_job_id,
                "language":st.session_state["language"],
                "ignore_existing":False,
                "summary_model": {
                    "modality":st.session_state["modality"],
                    "modelId": st.session_state["model_id"],
                    "provider": st.session_state["model_provider"],
                    "streaming":st.session_state["streaming"],
                    "model_kwargs":"{\n \"temperature\":"+str(st.session_state["temperature"])+",\"top_p\":"+str(st.session_state['top_p'])+",\"top_k\":"+str(st.session_state['top_k'])+"}"

                }
            }
        }
        return mutation_client.execute(Mutations.GENERATE_SUMMARY, "GenerateSummary", variables)

    return None

#========================================================================================
# [Controller] Manage realtime data subscriptions
#========================================================================================
#----------------------------------------------------------------------------------------
# Subscription callbacks
#----------------------------------------------------------------------------------------
def on_subscription_registered():
    """Callback when subscription is registered."""
    
    source_filename = st.session_state['uploaded_filename']
    if source_filename:
        generate_summary(source_filename)

def on_message_update(message, subscription_client):
    """Callback when summary job status update is received."""


    summary_response = message.get("updateSummaryJobStatus")
    print(f" summary_status:: {summary_response}")
    if not summary_response:
        return

    status = summary_response.get("status")
    print(f'status :: {status}') 
 
   
    # summary_widget = st.session_state['summary_widget']
    # text_height = st.session_state['summary_widget_height']
    
    if status == "New LLM token":
        encoded_summary = summary_response.get("summary")
        if not encoded_summary:
            return
    
        print("DISPLAY SUMMARY")
        print("========")
        summary_text = base64.b64decode(encoded_summary).decode("utf-8")
        st.session_state.summary_widget_text += summary_text
        summary_widget.text_area( '',st.session_state.summary_widget_text + " ▌",height=600)

        print("========")
        print(summary_text)
        print("========")
    elif status == "LLM streaming ended":
        file_processed=st.session_state['uploaded_filename']
        summary_generated=st.session_state.summary_widget_text
        st.session_state['file_processed']=file_processed
        st.session_state['summary_generated']=summary_generated
        subscription_client.unsubscribe()
    else:
        encoded_summary = summary_response.get("summary")
        if not encoded_summary:
            return
        summary_text = base64.b64decode(encoded_summary).decode("utf-8")
        summary_widget.text_area(f"Summary for **{st.session_state['uploaded_filename']}**", summary_text)
        subscription_client.unsubscribe()
    
#----------------------------------------------------------------------------------------
# Subscription registration
#----------------------------------------------------------------------------------------
def subscribe_to_summary_updates():
    """Subscribe to GraphQL subscription for summary job status updates."""

    if auth.is_authenticated():
        # Get user tokens
        access_token, id_token = auth.get_user_tokens()

        # Decode ID token
        decoded_token = auth.decode_id_token(id_token)

        # Get summary job ID

        summary_job_id = decoded_token.get("cognito:username", id_token[:10])
        
        # Subscribe to GraphQL subscription
        subscription_client = GraphQLSubscriptionClient(GRAPHQL_ENDPOINT, id_token)
        variables = {"summary_job_id": summary_job_id}
        summary_widget_text = ""
        st.session_state['summary_widget_text'] = summary_widget_text
        subscription_client.subscribe(
            Subscriptions.UPDATE_SUMMARY_JOB_STATUS,
            "UpdateSummaryJobStatus",
            variables,
            on_message_callback=on_message_update,
            on_subscription_registered_callback=on_subscription_registered
        )

#========================================================================================
# [View] Render UI components  
#========================================================================================

 # File uploader

   
def display_image(key):

    """Display image Streamlit."""
    print(f" pull image for  {key}")
    if key is not None:
        response = s3.get_object(Bucket=S3_INPUT_BUCKET, Key=key)
        file_stream = BytesIO(response['Body'].read())
        print('displaying image')
        st.text("")
        st.text("")
        st.image(file_stream,"Image")

    return response

# Streamlit page configuration

st.set_page_config(page_title="Summary", page_icon="🏷️", layout="wide", initial_sidebar_state="expanded")
add_indentation() 

hide_deploy_button()

# Check if user is authenticated and display login/logout buttons
auth = CognitoHelper() 
auth.set_session_state()
auth.print_login_logout_buttons()

# Logged in user UI
if auth.is_authenticated():
    credentials = auth.get_user_temporary_credentials()  
        
    s3 = boto3.client('s3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])


    print(f" authenticated user::") 
    with st.form("file-uploader", clear_on_submit=True):
        print(f" upload file started ::") 
        uploaded_file = st.file_uploader('Upload an image', type=['jpeg','png','jpg'])
        submitted = st.form_submit_button("Submit", use_container_width=True)
        st.session_state['progress_bar_widget'] = st.empty()
       
        print(f" file submitted:: {submitted}") 
        

        if  uploaded_file and submitted:
            s3.upload_fileobj(uploaded_file, S3_INPUT_BUCKET, uploaded_file.name)
            st.session_state['uploaded_filename'] = uploaded_file.name
            print(f" file uploaded:: {uploaded_file.name}")


            col1, col2 = st.columns(2)
            with col1:
                # width = int(st_javascript("window.innerWidth", key="pdf_width") - 20)  
                # height = int(width * 4/3)
                
                display_image(st.session_state['uploaded_filename'])

            with col2:
                # Display summary widget
                # text_width = int(st_javascript("window.innerWidth", key="text_width") - 20)
                # text_height = int(text_width * 3/4)

                summary_widget = st.empty()
                    
                
                if('file_processed' not in st.session_state): 
                    st.session_state['file_processed']=''
                #st.session_state.message_widget_text = ""
                # if summary_widget > 0:
                #     summary_widget.text_area(f"Summary for **{st.session_state['uploaded_filename']}**", height=height)
                #     st.session_state['summary_widget'] = summary_widget
                    #st.session_state['summary_widget_height'] = text_height

                print(f"file in session:: {st.session_state['file_processed']}")
                with st.spinner('Processing...'):
                    if (st.session_state['file_processed']==st.session_state['uploaded_filename']):
                        summary_text = st.session_state['summary_generated']    
                        summary_widget.text_area( '',summary_text + " ▌",height=600)
                        st.success(f"Summary for **{st.session_state['uploaded_filename']}**")
                    else:
                        subscribe_to_summary_updates()
                        st.success(f"Summary for **{st.session_state['uploaded_filename']}**")

        else:
             print("No file uploaded")


    
        
                    
                


# Guest user UI 
elif not auth.is_authenticated():
    st.info("Please login !")
    st.stop()
else:
    st.stop()


#########################
#        SIDEBAR
#########################

# sidebar

MODEL_ID_OPTIONS=['anthropic.claude-3-sonnet-20240229-v1:0',
                     'anthropic.claude-3-haiku-20240307-v1:0',
                     'anthropic.claude-v2:1',
                     'anthropic.claude-v2',
                     'anthropic.claude-instant-v1',
                     'amazon.titan-text-lite-v1',
                     'amazon.titan-text-express-v1',
                     'amazon.titan-text-premier-v1:0',
                     'IDEFICS']
MODEL_ID_PROVIDER=['Bedrock','Sagemaker']
LANGUAGE_OPTIONS=['English','Spanish','French']

with st.sidebar:
        st.header("Settings")
        st.subheader("Summarization Configuration")

        
        model_provider = st.selectbox(
                label="Select  model provider:",
                options=MODEL_ID_PROVIDER,
                key="model_provider",
                help="Select model provider.",
            )

        model_id = st.selectbox(
                label="Select model id:",
                options=MODEL_ID_OPTIONS,
                key="model_id",
                help="Select model type to generate summary.",
            )
       

        streaming = st.selectbox(
                label="Select streaming:",
                options=[True,False],
                key="streaming",
                help="Enable or disable streaming on response",
            )
        language = st.selectbox(
                label="Select language:",
                options=LANGUAGE_OPTIONS,
                key="language",
                help="Select response language",
            )
        
        modality = st.selectbox(
                label="Select modality:",
                options=["Image","Text"],
                key="modality",
                help="Select modality",
            )
       
        temperature = st.slider(
                label="Temperature:",
                value=1.0,
                min_value=0.0,
                max_value=1.0,
                key="temperature",
            )
        top_p = st.slider(
                label="Top P:",
                value=0.999,
                min_value=0.0,
                max_value=0.999,
                key="top_p",
            )
        top_k = st.slider(
                label="Top K:",
                value=250,
                min_value=0,
                max_value=500,
                key="top_k",
            )
            
