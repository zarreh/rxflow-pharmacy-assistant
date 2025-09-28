# RxFlow Conversation Logs Directory

This directory contains session-specific log files for RxFlow conversations.

## Log File Format
- Filename: `conversation_{session_id}_{timestamp}.log`
- Content: Complete conversation flow with timestamps, state transitions, user inputs, and AI responses

## Features
- 🔄 Automatic session logging for each conversation
- 📝 Detailed state machine transitions
- 💬 Full user input and AI response capture
- ⏰ Precise timestamps for all events
- 🔧 Session lifecycle tracking (start to end)

## Usage
Log files are automatically created when conversations start and are accessible through:
- Streamlit UI sidebar (📋 Session Logs section)
- Direct file access for debugging and analysis
- Session manager API methods

## File Management
- Log files are automatically created per session
- Each conversation gets a unique log file
- Files are closed and finalized when sessions end
- Old logs are preserved for analysis and debugging