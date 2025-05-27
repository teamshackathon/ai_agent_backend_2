#!/bin/bash

# Set script to exit on any error
set -e

# Function to display usage
usage() {
    echo "Usage: $0 <service> <message>"
    echo "Example: $0 discord 'AAGC2-123_タスク完了'"
    exit 1
}

# Check if required arguments are provided
if [ $# -ne 2 ]; then
    usage
fi

# Get arguments
service="$1"
message="$2"

# Extract number from message (AAGC2-number_something format)
number=""
if [[ "$message" =~ AAGC2-([0-9]+)_ ]]; then
    number="${BASH_REMATCH[1]}"
    echo "Extracted number: $number"
else
    echo "[Warning] Could not extract number from message: $message"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[Error] .env file not found."
    echo "Please download env from Google Drive: https://drive.google.com/xxxxx"
    exit 1
fi

# Load environment variables from .env file
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    if [[ -n "$key" && ! "$key" =~ ^[[:space:]]*# ]]; then
        # Remove any trailing whitespace/newlines and quotes from value
        value=$(echo "$value" | tr -d '\r\n' | sed 's/^"//; s/"$//')
        export "$key"="$value"
    fi
done < .env

if [ "$service" = "discord" ]; then
    # Set JSON file name
    JSON_FILE="response.json"
    
    # Notion API URL
    url="https://api.notion.com/v1/databases/${NOTION_DATABASE_ID}/query"
    
    # Get data from Notion API and save to JSON file
    curl -X POST \
      -H "Authorization: Bearer ${NOTION_API_KEY}" \
      -H "Notion-Version: 2022-06-28" \
      -H "Content-Type: application/json" \
      -d "{\"filter\": {\"property\": \"ID\",\"number\": {\"equals\": ${number}}}}" \
      "$url" > "$JSON_FILE"
    
    # Check if curl was successful
    if [ $? -ne 0 ]; then
        echo "[Error] Failed to fetch data from Notion API"
        exit 1
    fi
    
    # Replace Japanese property names with English ones
    sed -i '' 's/タスク名/task_name/g; s/担当者/assignee/g' "$JSON_FILE"
    
    # Extract data using jq
    if ! command -v jq &> /dev/null; then
        echo "[Error] jq is not installed. Please install jq first."
        echo "On Mac: brew install jq"
        exit 1
    fi
    
    task_name=$(jq -r '.results[0].properties.task_name.title[0].plain_text' "$JSON_FILE")
    assignee=$(jq -r '.results[0].properties.assignee.people[0].name' "$JSON_FILE")
    avatar_url=$(jq -r '.results[0].properties.assignee.people[0].avatar_url' "$JSON_FILE")
    notion_url=$(jq -r '.results[0].url' "$JSON_FILE")
    
    # Handle null avatar_url
    if [ "$avatar_url" = "null" ]; then
        avatar_url=""
    fi
    
    # Check if any results were found
    results_count=$(jq -r '.results | length' "$JSON_FILE")
    if [ "$results_count" -eq 0 ]; then
        echo "[Error] No record found with ID: $number"
        echo "Please check if the ID exists in the Notion database"
        exit 1
    fi
    
    # Check if data extraction was successful
    if [ "$task_name" = "null" ] || [ "$assignee" = "null" ]; then
        echo "[Error] Failed to extract data from Notion response"
        echo "Response content:"
        cat "$JSON_FILE"
        exit 1
    fi
    
    # Get current timestamp
    timestamp=$(date '+%Y/%m/%d %H:%M')
    
    # Generate random color (0-16777215)
    color=$((RANDOM * RANDOM % 16777216))
    
    # Prepare Discord embed JSON
    if [ -n "$avatar_url" ]; then
        discord_payload=$(cat <<EOF
{
  "embeds": [
    {
      "title": "【${message}】${task_name}",
      "color": ${color},
      "url": "${notion_url}",
      "author": {
        "name": "${assignee}",
        "icon_url": "${avatar_url}"
      },
      "footer": {
        "text": "${timestamp}"
      }
    }
  ]
}
EOF
)
    else
        discord_payload=$(cat <<EOF
{
  "embeds": [
    {
      "title": "【${message}】${task_name}",
      "color": ${color},
      "url": "${notion_url}",
      "author": {
        "name": "${assignee}"
      },
      "footer": {
        "text": "${timestamp}"
      }
    }
  ]
}
EOF
)
    fi
    
    # Send message to Discord
    discord_response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
         -H "Content-Type: application/json" \
         -X POST \
         -d "$discord_payload" \
         "$DISCORD_WEBHOOK")
    
    # Extract HTTP status code
    http_status=$(echo "$discord_response" | grep "HTTP_STATUS:" | cut -d: -f2)
    response_body=$(echo "$discord_response" | sed '/HTTP_STATUS:/d')
    
    if [ "$http_status" = "204" ] || [ "$http_status" = "200" ]; then
        echo "[Info] Message sent to Discord successfully"
    else
        echo "[Error] Failed to send message to Discord (HTTP $http_status)"
        echo "Response: $response_body"
        exit 1
    fi
    
    # Clean up temporary file
    if [ -f "$JSON_FILE" ]; then
        rm -f "$JSON_FILE"
        echo "[Info] Temporary file deleted: $JSON_FILE"
    fi
fi

echo "[Info] Script completed successfully" 