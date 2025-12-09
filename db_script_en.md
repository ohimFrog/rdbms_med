# Database Design - Presentation Script (English)

## Opening

> "Now, let me explain our database design. We designed our database following the **Third Normal Form (3NF)** to ensure data integrity and minimize redundancy."

---

## 1. Data Source & Collection

> "First, let me talk about our data source. We collected Korean pharmaceutical data from a public dataset. The original data was in CSV format, containing about **29,000 drug records** with size of approximately **10 megabytes**.
>
> The original CSV had 8 columns: product name, company name, effect, dosage, precautions, drug interactions, side effects, and storage instructions. All information was in Korean."

---

## 2. Why Normalization?

> "Initially, all this data was in a single flat table. This caused several problems:
>
> **First**, the manufacturer name was repeated for every single drug. If one company produces 100 drugs, the company name appears 100 times. This wastes storage space.
>
> **Second**, if we need to update a manufacturer's name, we would have to update thousands of rows. This is called an **update anomaly**.
>
> **Third**, storing related but separate concepts in one table violates the principle of **single responsibility**.
>
> To solve these problems, we applied **Third Normal Form normalization**."

---

## 3. Table-by-Table Explanation

### Table 1: manufacturer

> "The first table is **manufacturer**. This table stores information about pharmaceutical companies.
>
> It has two columns:
>
> - `id`: Primary key, auto-incremented integer
> - `name`: Company name, must be unique
>
> By separating manufacturers into their own table, we store each company name **only once**, no matter how many drugs they produce."

### Table 2: drug_basic

> "The second table is **drug_basic**. This is our central table that stores basic drug information.
>
> It has four columns:
>
> - `id`: Primary key
> - `name`: Drug product name
> - `manufacturer_id`: **Foreign key** referencing the manufacturer table
> - `storage`: Storage instructions
>
> Notice that instead of storing the manufacturer name directly, we store a reference to the manufacturer table. This is a **one-to-many relationship**: one manufacturer can have many drugs."

### Table 3: drug_usage

> "The third table is **drug_usage**. This stores the therapeutic information.
>
> - `id`: Primary key
> - `drug_id`: Foreign key to drug_basic, marked as **UNIQUE**
> - `effect`: What the drug is used for
> - `dosage`: How to take the medicine
>
> The **UNIQUE constraint** on drug_id ensures this is a **one-to-one relationship**. Each drug has exactly one usage record."

### Table 4: drug_warning

> "The fourth table is **drug_warning**. This contains safety-related information.
>
> - `id`: Primary key
> - `drug_id`: Foreign key, UNIQUE
> - `precaution`: General warnings and cautions
> - `interaction`: Drug interactions with other medicines
>
> Again, this is a **one-to-one relationship** with drug_basic."

### Table 5: drug_side_effect

> "The fifth table is **drug_side_effect**.
>
> - `id`: Primary key
> - `drug_id`: Foreign key, UNIQUE
> - `side_effect`: Possible adverse reactions
>
> This separation allows us to query side effect information independently when needed."

### Table 6: search_history

> "The sixth and final table is **search_history**. This logs user searches.
>
> - `id`: Primary key
> - `drug_id`: Foreign key to drug_basic
> - `searched_text`: The actual text the user searched for
> - `searched_at`: Timestamp of when the search occurred
>
> Note that drug_id here is **NOT unique**. This is a **one-to-many relationship**: one drug can be searched many times by different users."

---

## 4. Relationships Summary

> "Let me summarize the relationships in our database:
>
> - **Manufacturer to Drug**: One-to-Many. One manufacturer produces many drugs.
> - **Drug to Usage/Warning/SideEffect**: One-to-One. Each drug has exactly one of each.
> - **Drug to SearchHistory**: One-to-Many. One drug can have multiple search records.
>
> These relationships are enforced through **foreign key constraints**, ensuring referential integrity."

---

## 5. 3NF Verification

> "Let me verify that our design satisfies Third Normal Form:
>
> **First Normal Form**: All columns contain atomic values. No repeating groups.
>
> **Second Normal Form**: All non-key attributes are fully dependent on the primary key. We have no partial dependencies.
>
> **Third Normal Form**: There are no transitive dependencies. For example, manufacturer name no longer indirectly depends on drug_id through manufacturer_id.
>
> By achieving 3NF, we have eliminated data redundancy and ensured data consistency."

---

## 6. Benefits of This Design

> "This normalized design gives us several benefits:
>
> **First**, **Query Flexibility**. We can easily write JOIN queries to get related data. For example, getting all drugs from a specific manufacturer.
>
> **Second**, **Aggregation Capability**. We can use GROUP BY to get statistics, like counting how many drugs each manufacturer produces.
>
> **Third**, **Data Integrity**. Foreign key constraints prevent orphan records and maintain consistency.
>
> **Fourth**, **Scalability**. Adding new features, like tracking search history, only required adding one new table without modifying existing ones."

---

## Closing

> "In summary, we transformed a flat CSV file into a well-structured relational database with 6 tables, following 3NF principles. This design supports all the CRUD operations our application needs while maintaining data integrity and query efficiency.
>
> Now, let me show you the SQL queries we use in our application."
