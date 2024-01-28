from imports import *
from menu_logic import overview as overview_logic
from menu_logic import roles as roles_logic
from menu_logic import job as job_logic
from menu_logic import learn as learn_logic

pages = ["Home", "Overview", "Roles", "Learn", "Get Hired"]
page_icons = ["globe", "bar-chart-steps", "people", "book-half", "geo-alt"]

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

def write_json(path, data):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=2))


def filter_response(input, validate, system_prompt):
    human_prompt = """Only answer with [yes] for yes and [no] for no. Is $ a valid $?"""
    response = openai_template(system_prompt, human_prompt, [input, validate])
    
    if 'y' in response.lower():
        return True
    else:
        return False

    

st.title("Learnify\n")

selected = option_menu(
    menu_title=None,
    options=pages,
    icons=page_icons,
    orientation="horizontal"
)


if selected == "Overview":
    overview_logic()
if selected == "Learn":
    learn_logic()
if selected == "Roles":
    roles_logic()
if selected == "Get Hired":
    job_logic()

if selected == "Home":
    st.title("Home\n")

    with st.form(key='my_form'):
        career = st.text_input(label="Choose your career path", placeholder="Example: Computer Scientist", value="Computer Scientist")
        industry = st.text_input(label="Choose your industry", placeholder="Example: Finance", value="Finance")
        location = st.text_input(label="Where do you come from", placeholder="Example: London", value="London")
        submit_button = st.form_submit_button(label='Submit')


    if submit_button:
        
        system_prompt = """You are a career advisor."""
        move_on = True
        
        # Input Filters
        if not filter_response(career, "career", system_prompt) and move_on:
            st.write("That is not a valid career path.")
            move_on = False
        if not filter_response(industry, "industry", system_prompt) and move_on:
            st.write("That is not a valid industry.")
            move_on = False
        if not filter_response(location, "location", system_prompt) and move_on:
            st.write("That is not a valid location.")
            move_on = False
            
        if move_on:
            
            opportunity_prompt = """Generate me 5 roles in $ in the $ industry. Avoid repeating words. Short and concise."""
            opportunities = openai_template(opportunity_prompt, [career, industry])
            opportunities = re.findall(r'\d+\.\s*([^\d]+)', opportunities)
            
            learn_prompt = """Generate me categories to learn $ in the $ industry. Avoid repeating words. Short and concise"""
            learn = openai_template(learn_prompt, [career, industry])
            learn = re.findall(r'\d+\.\s*([^\d]+)', learn)
            
            new_data = {
                "learn": learn,
                "opportunity": opportunities,
                "career": career,
                "location": location,
                "industry": industry
            }
            
            write_json("./dataset.json", new_data)
            
            st.title(":red[Table of Contents]\n")
            
            st.markdown("## :orange[Overview]")
            st.markdown("### 1. Description\n### 2. Resources")
            
            st.write("\n\n")
            
            st.markdown("## :orange[Roles]")
            for i, x in enumerate(opportunities):
                st.markdown(f"### {i+1}. {x}")
            
            st.write("\n\n")
            
            st.markdown("## :orange[Learn]")
            for i, x in enumerate(learn):
                st.markdown(f"### {i+1}. {x}")
            
            st.write("\n\n")
            
            st.markdown("## :orange[Land a Job]")
            st.markdown("### 1. Linkedin Message Generator\n### 2. Resume Builder")
    
    
    