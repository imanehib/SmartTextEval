
import json
import time
from revision import revision_classification


class Revision:
    def __init__(self, start, end, position, text_before, text_end):
        self.index_start = start  # Placeholder for start index of the revision
        self.index_end = end    # Placeholder for end index of the revision
        self.start_point = position  #contextual or pre-contextual revision
        self.text_before = text_before         # Placeholder for the text of the revision
        self.text_end = text_end
        self.type = None  # Placeholder for revision type
        self.context = None
        self.reasoning = None  # Placeholder for reasoning behind classification
        self.instructions = None  # Placeholder for exercise instructions if needed
    
    
    def classify(self, client, assistant_id):
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Classify this revision:\nBefore: {self.text_before}\nAfter: {self.text_end}\nReturn JSON output."
        )

        # Run concerned assistant
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Retrieve response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response_text = messages.data[0].content[0].text.value
    

        try:
            clean_response_text = response_text.replace("```json", "").replace("```", "").strip()
            response = json.loads(clean_response_text)
            category = response['classification']
            reasoning_1 = response['reasoning']
            self.type = category
            self.reasoning = reasoning_1
            
        except json.JSONDecodeError:
            print("Error parsing first response:", response_text)
            exit()

        
        return self

    