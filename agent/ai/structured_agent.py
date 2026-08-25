from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(
    model = 'gemini-3.5-flash-lite',
    temperature = 0.2
)


class product_details(BaseModel):
    name : str = Field(description = 'name of the product', default = '')
    description : str = Field(description = 'related data about the product', default = '')
    price : int = Field(description = "price of the product", default = 0)
    category : str = Field(description = 'the category in which the product resides', default = '')
    stock : int = Field(description = 'quantity of product available for sale', default = 1)
    images : list[str] = Field(description = "image links of the product", default = [])
    
structured_prepare_products_llm = llm.with_structured_output(product_details)