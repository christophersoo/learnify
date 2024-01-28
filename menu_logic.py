from imports import *
import yt_dlp



def openai_template(human, *inputs):
    system_prompt = """You are a career advisor."""
    input_dict = {str(x): x for x in inputs}
    
    for x in inputs[0]:
        human = human.replace('$', f'{x}', 1)
    
    chat = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo-1106")
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run(input_dict)
    return result


def search_and_get_top_video_url(query):
    options = {
        'quiet': True,
        'format': 'best',  # Choose the best available quality
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        result = ydl.extract_info(f'ytsearch:{query}', download=False)
        if 'entries' in result and result['entries']:
            top_video_url = result['entries'][0]['url']
            return top_video_url
        else:
            return None

def read_json(path):
    with open(path, 'r') as f:
        data = json.loads(f.read())
    return data


def overview():
    data = read_json("./dataset.json")
    st.markdown("# :red[Overview]\n")
    
    human = f"""Give me the average salary of a $ based in $. No duplicate words. One sentence. In dollars. Per annum"""
    response = openai_template(human, [data["career"], data["location"]])
    response = re.sub(r'[^\d,]', '', response)
    
    st.markdown(f"## A :orange[{data['career'].capitalize()}] in :orange[{data['location'].capitalize()}]\n## on average makes around...")
    st.markdown(f"## :orange[${response}] USD per year\n")
    
    st.write("#")
    st.markdown("# :red[Short Video Introduction]\n")
    
    video_url = search_and_get_top_video_url(f"INTRODUCTION TO {data['career']} IN ENGLISH SIMPLE")
    st.video(video_url, "video/mp4")
    
    
    st.write('#')
    
    st.markdown(f'# :red[Description]\n')
    
    human2 = f"""Give me a brief description, responsibilities of a $ in the $ industry. No duplicate words. No headers. Only essay"""
    response2 = openai_template(human2, [data["career"], data["industry"]])
    
    st.markdown(f'### {response2}')
    
    st.write("#")
    
    human3 = f"""Give me a list of 10 textbooks to be a $ in the $ industry. No duplicate words. Bulletpoints. No essays"""
    response3 = openai_template(human3, [data["career"], data["industry"]])
    
    st.markdown(f'# :red[Online Resources]\n')
    
    response3 = re.split(r'\s*\d+\.\s*', response3)
    for i, x in enumerate(response3[1:]):
        st.markdown(f'### {i+1}. {x}')
    
        
        
def roles():
    data = read_json("./dataset.json")
    st.markdown("# :red[Roles]\n")
    st.write('#')
    
    for i, x in enumerate(data["opportunity"]):
        human = """Give me a brief description, responsibilities of a $ include their salary in $. No duplicate words. No headers. Only essay"""
        response = openai_template(human, [x, data['location']])
        
        st.markdown(f'## {i+1}. {x}\n')
        
        
        st.markdown(f'#### {response}')
        st.write('#')
        

def learn():
    data = read_json("./dataset.json")
    st.markdown("# :red[Learn]\n")
    st.write("#")
    
    for i, x in enumerate(data["learn"]):
        human = """give me a gentle introduction to $ without heading. If there are any math equations. Use latex and encapsulate them with dollar signs. If not, continue.
        In the format of a markdown file in html. Without any large containers."""
        response = openai_template(human, [x])
        
        st.markdown(f'## {i+1}. {x}\n')
        
        st.markdown(f' {response} ', unsafe_allow_html=True)
        st.write('#')


def compose_linkedin_message(interests, scraped, recipient, objective,):
    chat = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo-1106") # Here temperature is set to temp to provide a balanced response
    ### Template for the system message
    template = """
    You are a helpful AI assistant that supports people to send introduction messages on LinkedIn.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = f""""
    I am learning in the field of: {interests} Help me write a LinkedIn message, so that I can get a {objective}.

    Here is the LinkedIn description of the person I'm writing to:{recipient}

    Here is a webscrape of the company website: {scraped}

    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run({"interests": interests, "scraped": scraped, "recipient": recipient,"objective": objective})
    return result

def scrape_text_from_url(url):
    try:
        # Fetch the HTML content of the page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from the HTML
        text = soup.get_text(separator='\n', strip=True)
        
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content: {e}")
        return None




def job():
    data = read_json("./dataset.json")
    st.markdown("# :red[Get Hired]\n")
    
    st.write("#")
    
    st.markdown("# :red[Linkedin Message Generator]\n")
    with st.form("linkedin_message"):
        interests = st.text_input("What are your interests?")
        weblink = st.text_input("Input your target company's website")
        hr_lead = st.text_input("What's the LinkedIn of the HR Lead")
        objectives = selected_option = st.selectbox(
        "Choose an option",
        ("Internship", "Full-Time Job", "To chat further")
        )
        

        formsumbit = st.form_submit_button("Submit")

    if formsumbit:
        webscrape = scrape_text_from_url(weblink)
        with st.expander("Click to see webscrape"):
            st.write(webscrape)

        with st.spinner():
            message = compose_linkedin_message(interests, webscrape, hr_lead,objectives)
        
        st.write(message)
    
    st.write("#")
    st.markdown("# :red[Resume Builder]\n")
    
    with st.form(key='my_form'):
        name = st.text_input(label="What's your name?")
        email = st.text_input(label="What's your email address?")
        education = st.text_area(label="What is your educational background?")
        experience = st.text_area("What is your experience?")
        skills = st.text_input("What are your primary skills?")
        submit_button = st.form_submit_button(label='Submit')

    with st.spinner():
        if submit_button:
            human = f""""generate me a template resume for a career in $ in the $ industry in $, The resume should include who is $, $, $, $, $. 
            Use the one column template for the cv. It should be written in Overleaf format. Full latex. No english. Only latex"""
            response = openai_template(human, [data["career"], data["industry"], data["location"], name, email, education, experience, skills])
            st.markdown(response)