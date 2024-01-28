import streamlit as st
import re
import os
import json
import requests
import streamlit as st
from streamlit_option_menu import option_menu
import openai
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from apikey import openaikey
from bs4 import BeautifulSoup
import subprocess
openai.api_key = openaikey
os.environ['OPENAI_API_KEY'] = openaikey
