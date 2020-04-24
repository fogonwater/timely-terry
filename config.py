# The string that Terry will identify himself
USER_AGENT = "Timely Terry/0.1"

# Terry uses Slack "webhooks" to POST messages to a specific channel.
# The URL below is placeholder for you to edit — it won't work as is.
# See https://api.slack.com/messaging/webhooks for instructions
# on how to setting up a Slack webhook URL.
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"

# A list of urls to monitor and labels for Terry to announce.
# Replace these with the websites you want to monitor.
PAGES = [
    {"label": "RNZ", "url": "https://www.rnz.co.nz/"},
    {"label": "The Spinoff", "url": "https://thespinoff.co.nz/"}
]

# Specify number of seconds Terry will sleep between checks.
CHECK_FREQUENCY = 60