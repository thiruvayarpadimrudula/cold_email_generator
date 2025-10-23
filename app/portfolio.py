import pandas as pd
import chromadb
import uuid
from typing import Optional


class Portfolio:
    def __init__(self, file_path: str = "app/resource/my_portfolio.csv"):
        """
        file_path: default CSV loaded when no upload is provided.
        self.data will be a pandas DataFrame.
        """
        self.file_path = file_path
        try:
            self.data = pd.read_csv(file_path)
        except Exception:
            # If default file missing or unreadable, start with empty DataFrame
            self.data = pd.DataFrame(columns=["Techstack", "Links"])

        # Create/attach to a persistent Chroma client and a named collection.
        # We keep the collection name stable unless user uploads a new portfolio,
        # in which case load_portfolio will create a fresh collection.
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self, uploaded_df: Optional[pd.DataFrame] = None):
        """
        Load portfolio into Chroma. If uploaded_df is provided, create a fresh
        collection (unique name) and load the uploaded data. Otherwise, load the
        default CSV only if collection is empty.
        """
        if uploaded_df is not None:
            # Validate uploaded dataframe has required columns
            if not {"Techstack", "Links"}.issubset(set(uploaded_df.columns)):
                raise ValueError("Uploaded CSV must contain 'Techstack' and 'Links' columns.")
            self.data = uploaded_df.copy()
            # create a fresh collection name to avoid duplicates
            new_name = f"portfolio_{uuid.uuid4().hex}"
            self.collection = self.chroma_client.get_or_create_collection(name=new_name)

        # Add entries only if collection is empty (prevents re-adding on repeated calls)
        if not self.collection.count():
            for _, row in self.data.iterrows():
                tech = str(row.get("Techstack", "")) if not pd.isna(row.get("Techstack", "")) else ""
                link = str(row.get("Links", "")) if not pd.isna(row.get("Links", "")) else ""
                # Only add if at least one field present
                if not tech and not link:
                    continue
                self.collection.add(
                    documents=[tech],               # must be a list
                    metadatas=[{"links": link}],   # must be a list of dicts
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        """
        skills: list or string
        returns a list of dicts like [{'links': 'https://...'}, ...]
        """
        if isinstance(skills, str):
            skills = [skills]
        try:
            results = self.collection.query(query_texts=skills, n_results=2).get('metadatas', [[]])
        except Exception:
            # In case collection or query fails, return empty list
            return []

        # Flatten results to [{'links': ...}, ...]
        top_links = []
        for sublist in results:
            for r in sublist:
                if isinstance(r, dict) and 'links' in r:
                    top_links.append({'links': r['links']})
                elif isinstance(r, str):
                    top_links.append({'links': r})
        return top_links
