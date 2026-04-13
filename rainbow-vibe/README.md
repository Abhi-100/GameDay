# Install dependencies
pip install -r requirements.txt

# Create RainbowVibeExecutionRole
sh create_iam_role.sh

# Create a knowledge base using the PDFs in /data 
folder and update market_maven_agent.py with your Knowledge Base ID. Provide your Knowledge Base ID for scoring

# Double check profit_potion_agent.py has the correct RainbowVibeHouseProjects DynamoDB table name

# Create an S3 bucket to store images, update sparkle_design_agent with the S3 bucket name

# Fix TODOs in all agent python files

# Deploy the agent
agentcore configure --entrypoint harmony_swarm_agent.py --execution-role your_role_arn
agentcore launch
agentcore invoke '{"prompt": "Hello"}'  

# Provide your agentcore arn for scoring

# Launch the streamlit_rainbowvibe.py
streamlit run streamlit_rainbowvibe.py

# You can test your agentcore with sample questions using streamlit_rainbowvibe.py to assess your agent readiness for scoring
Remember that my favorite design style is modern minimalist and luxurious
create an image of a bathroom
What is the median new residential sale price in July 2025?
I am considering moving to Las Vegas. What are the things I should know before moving.
How much profit would I make for my house projects that are estimated to complete in June, give me a breakdown of your calculation
Remember that I change my mind that my new favorite design style is fun with rainbow and unicorn vibe
Create an image of a bedroom for kids
I am looking to remodel my bathroom, give me some design ideas
Apartments that do not accept Section 8
How is my property tax calculated if my home's market value is $400,000, the assessment ratio is 50%, and the total millage rate is 25 mills? Show me the steps
Does an inground pool always raise property taxes?
A family buys a new house with a market value of $400,000 that assesses property at 35% of its value. What is the initial property tax?


# Add Long memory to harmony_swarm_agent.py

# Redeploy the agent

# Click Ready for scoring

# Create a fair housing guardrail, add the guardrail configuration to harmony_swarm_agent 

# Redeploy the agent

# Provide ARN again for scoring



