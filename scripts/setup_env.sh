#!/bin/bash

# Check if API key is provided as argument
if [ -z "$1" ]; then
    echo "Please provide your OpenAI API key as an argument"
    echo "Usage: ./setup_env.sh YOUR_API_KEY"
    exit 1
fi

# Create .env file
echo "OPENAI_API_KEY=$1" > .env

# Export environment variable
export OPENAI_API_KEY=$1

echo "Environment variables set up successfully!"
echo "You can now run the theorem prover with: python -m src.main" 