#!/usr/bin/env python3
# Temporary script to convert the test sample to CSV format
import csv
import json
import os

# Sample data from test_haiven_rag.py
sample = {
    "user_input": "What are privacy-enhancing technologies?",
    "response": """Privacy Enhancing Technologies (PETs) are designed to offer greater privacy or secrecy for individuals whose data is being processed, stored, and collected by systems and software. These technologies help modify traditional data handling practices, ensuring users' data is not hoarded in raw or plaintext form. PETs facilitate user choice and genuine privacy by providing a better understanding of and better execution of privacy technology.

Key Points:

Definition: PETs are technologies that improve the privacy and secrecy of data processing.
Application: These technologies are used during data processing to handle user data more securely and privately.
Shift to Production: Initially developed in research labs, PETs have transitioned to production systems in recent years.
Broader Impact: While PETs are important, privacy also encompasses personal, social, cultural, and political aspects.
Further Exploration:

Privacy by Design: Incorporating privacy considerations from the outset of the product design.
Privacy and Security Engineering: Deepening knowledge in fields that tackle privacy and security comprehensively.
Remember, privacy technology is a tool among many to address societal inequalities in privacy and power. It should not replace thoughtful approaches to these complex issues.""",
    "reference": "Privacy Enhancing Technologies (PETs) are technologies that provide increased privacy or secrecy for the persons whose data is processed, stored and/or collected by software and systems. Three PETs that are valuable and ready for use are: Differential Privacy, Distributed & Federated Analysis & Learning, and Encrypted Computation. They provide rigorous guarantees for privacy and as such are becoming increasingly popular to provide data in while minimizing violations of private data.",
    "retrieved_contexts": [
        """Privacy Enhancing Technologies are in the news fairly regularly, with
    open calls from NIST and the UK
    government,
    Singapore and
    Europe
    to determine how and where these technologies can and should be used. As a
    developer, architect or technologist, you might have already heard about or
    even used these technologies, but your knowledge might be outdated, as
    research and implementations have shifted significantly in recent years.""",
        """What are PETs?
Privacy Enhancing Technologies (from hereon: PETs) are technologies that
      provide increased privacy or secrecy for the persons whose data is processed,
      stored and/or collected by software and systems. These technologies are often
      used as a part of this processing and modify the normal ways of handling (and
      often, hoarding) raw or plaintext data directly from users and internal""",
        """they implement data systems—enabling user choice and real privacy through
    better understanding of privacy technology.
A final note: privacy is much more than technology. It's personal, social,
    cultural and political. Applying technology to societal problems is often
    naive and even dangerous. Privacy technology is one tool of many to help
    address real inequalities in access to privacy and power in the world. It""",
        """options.
Privacy technologies are one way to align the needs of data science with
        those of user consent, awareness and privacy. Until recent years, these
        technologies were mainly in research and innovation labs. In the past 5 years,
        they've moved out of the lab and into production systems. These are not the
        only ways to provide people with better privacy, but they're a good start for""",
        """this article, you'll learn the basic technical aspects of privacy to enable
      more choices for users to navigate their identity and information when they
      interact with systems. There are, of course, many other aspects to building
      privacy into products. For now, these are out-of-scope for this article, but I
      can highly recommend exploring Privacy by
      Design
      and diving deeper into the fields of privacy and security engineering.""",
    ]
}

# CSV file path
csv_file_path = os.path.join(os.path.dirname(__file__), 'test_data', 'rag_samples.csv')

# Write to CSV with proper escaping
with open(csv_file_path, 'w', newline='') as csvfile:
    # Write the header row
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    writer.writerow(['user_input', 'response', 'reference', 'retrieved_contexts'])
    
    # Write the data row
    writer.writerow([
        sample["user_input"],
        sample["response"],
        sample["reference"],
        json.dumps(sample["retrieved_contexts"])  # Convert list to JSON string
    ])

print(f"Sample data has been written to {csv_file_path}")