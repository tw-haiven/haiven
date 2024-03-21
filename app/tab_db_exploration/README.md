### Demo notes
This demo showcases the capabilities of GenAI to create SQL queries on the fly from natural language. The prompt is aware of the schema displayed on the left, which is automatically determined from the sample database. 

[Video Recording](https://storage.cloud.google.com/genai-demo-large-files/teamai-recording-db-exploration.mp4)

**Benefits:**
- Onboarding: Allows new team members to more quickly explore the structure of the application database, and how to query it.
- Debugging: Supports developers when they are debugging data constellations in the test database
- Enablement of non-technical users: Allows stakeholders and testers to explore the contents of test environment databases without having to know the schema, or SQL

**Risks and caveats:**
- Data quality: How well this works depends on the complexity of the database schema, and the expressiveness of the schema's field and table names. The more those names match the domain language, the easier it is for the language model to translate questions into SQL queries.
