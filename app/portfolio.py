# import pandas as pd
# import chromadb
# import uuid
# from typing import Optional


# class Portfolio:
#     def __init__(self, file_path: str = "app/resource/my_portfolio.csv"):
#         """
#         file_path: default CSV loaded when no upload is provided.
#         self.data will be a pandas DataFrame.
#         """
#         self.file_path = file_path
#         try:
#             self.data = pd.read_csv(file_path)
#         except Exception:
#             # If default file missing or unreadable, start with empty DataFrame
#             self.data = pd.DataFrame(columns=["Techstack", "Links"])

#         # Create/attach to a persistent Chroma client and a named collection.
#         # We keep the collection name stable unless user uploads a new portfolio,
#         # in which case load_portfolio will create a fresh collection.
#         self.chroma_client = chromadb.PersistentClient('vectorstore')
#         self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

#     def load_portfolio(self, uploaded_df: Optional[pd.DataFrame] = None):
#         """
#         Load portfolio into Chroma. If uploaded_df is provided, create a fresh
#         collection (unique name) and load the uploaded data. Otherwise, load the
#         default CSV only if collection is empty.
#         """
#         if uploaded_df is not None:
#             # Validate uploaded dataframe has required columns
#             if not {"Techstack", "Links"}.issubset(set(uploaded_df.columns)):
#                 raise ValueError("Uploaded CSV must contain 'Techstack' and 'Links' columns.")
#             self.data = uploaded_df.copy()
#             # create a fresh collection name to avoid duplicates
#             new_name = f"portfolio_{uuid.uuid4().hex}"
#             self.collection = self.chroma_client.get_or_create_collection(name=new_name)

#         # Add entries only if collection is empty (prevents re-adding on repeated calls)
#         if not self.collection.count():
#             for _, row in self.data.iterrows():
#                 tech = str(row.get("Techstack", "")) if not pd.isna(row.get("Techstack", "")) else ""
#                 link = str(row.get("Links", "")) if not pd.isna(row.get("Links", "")) else ""
#                 # Only add if at least one field present
#                 if not tech and not link:
#                     continue
#                 self.collection.add(
#                     documents=[tech],               # must be a list
#                     metadatas=[{"links": link}],   # must be a list of dicts
#                     ids=[str(uuid.uuid4())]
#                 )

#     def query_links(self, skills):
#         if isinstance(skills, str):
#                 skills = [skills]
        
#         skills = [
#             skill.strip()
#             for skill in skills
#             if isinstance(skill, str) and skill.strip()
#         ]
        
#         if not skills or self.collection.count() == 0:
#             return []
        
#         try:
#             results = self.collection.query(
#                 query_texts=skills,
#                 n_results=2
#             )
        
#             metadatas = results.get("metadatas", [])
#             documents = results.get("documents", [])
#         except Exception as e:
#             print(f"Portfolio search failed: {e}")
#             return []
        
#         top_projects = []
#         seen_links = set()
        
#         for metadata_group, document_group in zip(metadatas, documents):
#             for metadata, techstack in zip(metadata_group, document_group):
#                 link = metadata.get("links", "") if metadata else ""
        
#                 if not link or link in seen_links:
#                     continue
        
#                 seen_links.add(link)
        
#                 top_projects.append({
#                     "techstack": techstack or "",
#                     "links": link
#                 })
        
#         return top_projects

    
# import pandas as pd
# import chromadb
# import uuid
# from typing import Optional


# class Portfolio:

#     def __init__(self, file_path: str = "app/resource/my_portfolio.csv"):

#         self.file_path = file_path

#         try:
#             self.data = pd.read_csv(file_path)

#         except Exception:
#             self.data = pd.DataFrame(
#                 columns=["Title", "Techstack", "Links", "Description"]
#             )

#         self.chroma_client = chromadb.PersistentClient(
#             path="vectorstore"
#         )

#         self.collection = self.chroma_client.get_or_create_collection(
#             name="portfolio"
#         )

    
#     def load_portfolio(self, uploaded_df: Optional[pd.DataFrame] = None):

#         if uploaded_df is not None:
#             self.data = uploaded_df.copy()

#         # Validate required columns
#         required_columns = {"Techstack", "Links"}
#         if not required_columns.issubset(self.data.columns):
#             raise ValueError("CSV must contain Techstack and Links.")

#         for column in ["Title", "Description"]:
#             if column not in self.data.columns:
#                 self.data[column] = ""

#     # Refresh the existing collection
#         self.chroma_client.delete_collection("portfolio")
    
#         self.collection = self.chroma_client.create_collection(
#             name="portfolio"
#         )

#         documents = []
#         metadatas = []
#         ids = []

#         for _, row in self.data.iterrows():

#             title = self._clean_value(row.get("Title", ""))
#             techstack = self._clean_value(row.get("Techstack", ""))
#             description = self._clean_value(row.get("Description", ""))
#             link = self._clean_value(row.get("Links", ""))

#             if not any([title, techstack, description, link]):
#                 continue

#             document = f"""
#             Project: {title}
#             Technologies: {techstack}
#             Description: {description}
#             """

#             documents.append(document.strip())

#             metadatas.append({
#                 "title": title,
#                 "techstack": techstack,
#                 "description": description,
#                 "links": link
#             })

#             ids.append(str(uuid.uuid4()))

#         if documents:
#             self.collection.add(
#                 documents=documents,
#                 metadatas=metadatas,
#                 ids=ids
#             )

#         print("CSV projects:", len(self.data))
#         print("ChromaDB projects:", self.collection.count())


#     @staticmethod
#     def _clean_value(value):

#         if value is None or pd.isna(value):
#             return ""

#         return str(value).strip()

#     def query_links(self, skills):

#         if isinstance(skills, str):
#             skills = [skills]

#         skills = [
#             skill.strip()
#             for skill in skills
#             if isinstance(skill, str) and skill.strip()
#         ]

#         if not skills or self.collection.count() == 0:
#             return []

#         try:

#             results = self.collection.query(
#                 query_texts=skills,
#                 n_results=min(2, self.collection.count()),
#                 include=["documents", "metadatas", "distances"]
#             )

#             metadatas = results.get("metadatas", [])
#             distances = results.get("distances", [])

#         except Exception as e:

#             print(f"Portfolio search failed: {e}")
#             return []

#         top_projects = []
#         seen_links = set()

#         for metadata_group, distance_group in zip(
#             metadatas, distances
#         ):

#             for metadata, distance in zip(
#                 metadata_group, distance_group
#             ):

#                 if not metadata:
#                     continue

#                 link = metadata.get("links", "")

#                 # Avoid duplicate projects
#                 if not link or link in seen_links:
#                     continue

#                 seen_links.add(link)

#                 top_projects.append({
#                     "title": metadata.get("title", ""),
#                     "techstack": metadata.get("techstack", ""),
#                     "description": metadata.get("description", ""),
#                     "links": link,
#                     "distance": distance
#                 })

#         return top_projects




import pandas as pd
import chromadb
import uuid
import hashlib
import time
from collections import OrderedDict, namedtuple
from functools import lru_cache
from typing import Optional


class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path

        try:
            self.data = pd.read_csv(file_path)
        except Exception:
            self.data = pd.DataFrame(
                columns=["Title", "Techstack", "Links", "Description"]
            )

        self.chroma_client = chromadb.PersistentClient(path="vectorstore")
        self.collection = None
        self._loaded = False
        self._embedding_cache = OrderedDict()
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_maxsize = 256

    def load_portfolio(self, uploaded_df: Optional[pd.DataFrame] = None, csv_path: Optional[str] = None):
        # Use uploaded data when provided; otherwise retain the current data.
        if uploaded_df is not None:
            self.data = uploaded_df.copy()
            self._loaded = False
        elif csv_path is not None:
          self.data = pd.read_csv(csv_path)
          self._loaded = False
        # Do not rebuild the same portfolio on every Streamlit submission.
        if self._loaded:
            return

        required_columns = {"Techstack", "Links"}
        if not required_columns.issubset(self.data.columns):
            raise ValueError("CSV must contain Techstack and Links columns.")

        for column in ["Title", "Description"]:
            if column not in self.data.columns:
                self.data[column] = ""

        # Create a stable collection name based on the CSV contents.
        csv_content = self.data.fillna("").astype(str).to_csv(index=False)
        fingerprint = hashlib.sha256(
            csv_content.encode("utf-8")
        ).hexdigest()[:12]

        collection_name = f"portfolio_{fingerprint}"

        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name
        )

        # Populate only when this collection is new and empty.
        if self.collection.count() == 0:
            documents = []
            metadatas = []
            ids = []

            for _, row in self.data.iterrows():
                title = self._clean_value(row.get("Title", ""))
                techstack = self._clean_value(row.get("Techstack", ""))
                description = self._clean_value(row.get("Description", ""))
                link = self._clean_value(row.get("Links", ""))

                if not any([title, techstack, description, link]):
                    continue

                document = (
                    f"Project: {title}\n"
                    f"Technologies: {techstack}\n"
                    f"Description: {description}"
                )

                documents.append(document)
                metadatas.append({
                    "title": title,
                    "techstack": techstack,
                    "description": description,
                    "links": link
                })
                ids.append(str(uuid.uuid4()))

            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

        # Clear old cached embeddings when switching portfolio collections.

        self._loaded = True

        print("Portfolio projects:", len(self.data))
        print("ChromaDB projects:", self.collection.count())

    @staticmethod
    def _clean_value(value):
        if value is None or pd.isna(value):
            return ""
        return str(value).strip()

    
    
    
    def _get_batch_embeddings(self, skills):
        embeddings = {}
        missing_skills = []

        for skill in skills:
            if skill in self._embedding_cache:
                self._cache_hits += 1

                embedding = self._embedding_cache.pop(skill)
                self._embedding_cache[skill] = embedding

                embeddings[skill] = list(embedding)
            else:
                self._cache_misses += 1
                missing_skills.append(skill)

        if missing_skills:
            embedding_function = self.collection._embedding_function

            new_embeddings = embedding_function(missing_skills)

            for skill, embedding in zip(missing_skills, new_embeddings):
                embedding = tuple(float(x) for x in embedding)

                self._embedding_cache[skill] = embedding
                embeddings[skill] = list(embedding)

                if len(self._embedding_cache) > self._cache_maxsize:
                    self._embedding_cache.popitem(last=False)

        return [embeddings[skill] for skill in skills]

    def get_embedding_cache_info(self):
        CacheInfo = namedtuple(
            "CacheInfo",
            ["hits", "misses", "maxsize", "currsize"]
        )

        return CacheInfo(
            self._cache_hits,
            self._cache_misses,
            self._cache_maxsize,
            len(self._embedding_cache)
        )


    
    
    
    def query_links(self, skills):

        if isinstance(skills, str):
            skills = [skills]

        skills = list(dict.fromkeys(
            skill.strip()
            for skill in skills
            if isinstance(skill, str) and skill.strip()
        ))

        if not skills or self.collection is None:
            return []

        count = self.collection.count()

        if count == 0:
            return []

        try:
        # Generate missing embeddings in one batch
            embedding_start = time.perf_counter()

            query_embeddings = self._get_batch_embeddings(skills)

            embedding_time = time.perf_counter() - embedding_start

        # Perform one batch ChromaDB query
            search_start = time.perf_counter()

            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=min(2, count),
                include=["documents", "metadatas", "distances"]
            )

            search_time = time.perf_counter() - search_start

            print(f"Skills searched: {len(skills)}")
            print(f"Batch embedding time: {embedding_time:.4f} sec")
            print(f"ChromaDB search time: {search_time:.4f} sec")

            metadatas = results.get("metadatas", [])
            distances = results.get("distances", [])

        except Exception as e:
            import traceback
            print("Portfolio search failed:")
            traceback.print_exc()
            return []

        top_projects = []
        seen_links = set()

        for metadata_group, distance_group in zip(metadatas, distances):

            for metadata, distance in zip(metadata_group, distance_group):

                if not metadata:
                    continue

                link = metadata.get("links", "")

                if not link or link in seen_links:
                    continue

                seen_links.add(link)

                top_projects.append({
                    "title": metadata.get("title", ""),
                    "techstack": metadata.get("techstack", ""),
                    "description": metadata.get("description", ""),
                    "links": link,
                    "distance": distance
                })

        print("Embedding cache:", self.get_embedding_cache_info())

      
      
        return top_projects
