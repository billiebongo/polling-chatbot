# Telegram polling bot
- YoN is a pollbot who helps members in a channel facilitate polling. Gather feedback for your ideas easily with this polling bot!

# How this works
- Master creates a channel in Telegram and add members into the channel
- Master creates a google sheet which would store all poll results
- Members can chat with poll_bot and follow the commands to create/retrieve their queries
- Members can attach image and further elaboration on their vote. 
- Members can retrieve poll results for their polls from other members in the chat with poll_bot. They cannot retrieve poll results for queries that is not theirs as the user_id is recorded for each user.
- Members can answer to polls by clicking on queries on the channel announced by poll_bot


#Requirements
- Replace telegram bot API_KEY and google sheets API_KEY in the source code
- Create a virtual environment and `pip install -r requirements`




