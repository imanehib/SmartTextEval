#!/usr/bin/env bash
cd "$(dirname "$0")/LanguageTool/LanguageTool-6.5"
java -jar languagetool-server.jar --port 8081
