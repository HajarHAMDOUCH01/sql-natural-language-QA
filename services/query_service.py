import os
from typing import Dict, Any
from fastapi import HTTPException
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from models.schemas import (
    QueryResponse, 
    Query, 
    QueryResult, 
    GeneratedAnswer, 
    APIKeys,
    DatabaseFile
)


class QueryService:
    def __init__(self):
        """Initialize QueryService without dependencies"""
        pass

    async def process_question(
        self, 
        question: str, 
        session_id: str, 
        db_path: str, 
        api_keys: APIKeys
    ) -> Dict[str, Any]:
        """
        Complete pipeline: question -> SQL query -> execute -> generate answer
        """
        try:
            # Set environment variables for API keys
            os.environ["GOOGLE_API_KEY"] = api_keys.gemini_api_key
            os.environ["LANGSMITH_API_KEY"] = api_keys.langchain_api_key
            os.environ["LANGSMITH_TRACING"] = "true"
            
            # Initialize database connection
            db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
            
            # Initialize LLM
            llm = init_chat_model("gemini-2.5-pro", model_provider="google_genai")
            
            # Step 1: Convert question to SQL query
            sql_query = await self._generate_sql_query(question, db, llm)
            
            # Step 2: Execute the SQL query
            query_result = await self._execute_query(sql_query, db)
            
            # Step 3: Generate natural language answer
            final_answer = await self._generate_answer(
                question, sql_query, query_result, llm
            )
            
            return {
                "session_id": session_id,
                "question": question,
                "sql_query": sql_query,
                "query_result": query_result,
                "answer": final_answer
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing question: {str(e)}"
            )

    async def _generate_sql_query(
        self, 
        question: str, 
        db: SQLDatabase, 
        llm
    ) -> str:
        """Generate SQL query from natural language question"""
        try:
            system_message = """
            Given an input question, create a syntactically correct {dialect} query to
            run to help find the answer. Unless the user specifies in his question a
            specific number of examples they wish to obtain, always limit your query to
            at most {top_k} results. You can order the results by a relevant column to
            return the most interesting examples in the database.

            Never query for all the columns from a specific table, only ask for a the
            few relevant columns given the question.

            Pay attention to use only the column names that you can see in the schema
            description. Be careful to not query for columns that do not exist. Also,
            pay attention to which column is in which table.

            Only use the following tables:
            {table_info}
            """
            
            query_prompt_template = ChatPromptTemplate([
                ("system", system_message), 
                ("user", "{input}")
            ])
            
            prompt = query_prompt_template.invoke({
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": question
            })
            
            structured_llm = llm.with_structured_output(QueryResponse)
            result = structured_llm.invoke(prompt)
            
            return result.query
            
        except Exception as e:
            raise Exception(f"Error generating SQL query: {str(e)}")

    async def _execute_query(self, sql_query: str, db: SQLDatabase) -> str:
        """Execute the generated SQL query"""
        try:
            execute_query_tool = QuerySQLDatabaseTool(db=db)
            result = execute_query_tool.invoke(sql_query)
            return result
            
        except Exception as e:
            raise Exception(f"Error executing SQL query: {str(e)}")

    async def _generate_answer(
        self, 
        question: str, 
        sql_query: str, 
        query_result: str, 
        llm
    ) -> str:
        """Generate natural language answer from query results"""
        try:
            prompt = (
                "Given the following user question, corresponding SQL query, "
                "and SQL result, answer the user question.\n\n"
                f"Question: {question}\n"
                f"SQL Query: {sql_query}\n"
                f"SQL Result: {query_result}"
            )
            
            response = llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")

    # Optional: Keep individual methods for flexibility
    def generate_sql_query_only(
        self, 
        question: str, 
        db: SQLDatabase, 
        api_keys: APIKeys
    ) -> Query:
        """Generate only SQL query (for testing or separate usage)"""
        try:
            os.environ["GOOGLE_API_KEY"] = api_keys.gemini_api_key
            llm = init_chat_model("gemini-2.5-pro", model_provider="google_genai")
            
            system_message = """
            Given an input question, create a syntactically correct {dialect} query to
            run to help find the answer. Unless the user specifies in his question a
            specific number of examples they wish to obtain, always limit your query to
            at most {top_k} results. You can order the results by a relevant column to
            return the most interesting examples in the database.

            Never query for all the columns from a specific table, only ask for a the
            few relevant columns given the question.

            Pay attention to use only the column names that you can see in the schema
            description. Be careful to not query for columns that do not exist. Also,
            pay attention to which column is in which table.

            Only use the following tables:
            {table_info}
            """
            
            query_prompt_template = ChatPromptTemplate([
                ("system", system_message), 
                ("user", "{input}")
            ])
            
            prompt = query_prompt_template.invoke({
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": question
            })
            
            structured_llm = llm.with_structured_output(QueryResponse)
            result = structured_llm.invoke(prompt)
            
            return Query(
                session_id="", # Will be set by caller
                query=result
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating SQL query: {str(e)}"
            )

    def execute_sql_query(self, sql_query: str, db: SQLDatabase) -> QueryResult:
        """Execute SQL query and return result"""
        try:
            execute_query_tool = QuerySQLDatabaseTool(db=db)
            result = execute_query_tool.invoke(sql_query)
            return QueryResult(result=[result])
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error executing query: {str(e)}"
            )

    def generate_natural_answer(
        self, 
        question: str,
        query: str, 
        result: str,
        api_keys: APIKeys
    ) -> GeneratedAnswer:
        """Generate natural language answer from query results"""
        try:
            os.environ["GOOGLE_API_KEY"] = api_keys.gemini_api_key
            llm = init_chat_model("gemini-2.5-pro", model_provider="google_genai")
            
            prompt = (
                "Given the following user question, corresponding SQL query, "
                "and SQL result, answer the user question.\n\n"
                f"Question: {question}\n"
                f"SQL Query: {query}\n"
                f"SQL Result: {result}"
            )
            
            response = llm.invoke(prompt)
            return GeneratedAnswer(answer=response.content)
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating answer: {str(e)}"
            )