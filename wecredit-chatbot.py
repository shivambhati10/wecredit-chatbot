import openai
import re
import json
import os
from datetime import datetime

# Configuration
class Config:
    def __init__(self):
        self.model = "gpt-3.5-turbo"  
        self.api_key = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
        self.max_tokens = 150
        self.temperature = 0.7


class KnowledgeBase:
    def __init__(self):
        self.financial_concepts = {
            "loan": {
                "definition": "A sum of money borrowed that is expected to be paid back with interest",
                "types": ["Personal Loan", "Home Loan", "Auto Loan", "Education Loan", "Business Loan"],
                "documentation": ["ID Proof", "Address Proof", "Income Proof", "Bank Statements"]
            },
            "interest rate": {
                "definition": "The amount charged by a lender to a borrower for the use of assets",
                "types": ["Fixed Rate", "Floating Rate", "Flat Rate"],
                "calculation": "Interest = Principal × Rate × Time"
            },
            "credit score": {
                "definition": "A numerical expression based on a statistical analysis of a person's credit files",
                "range": "300-900 in India (CIBIL Score)",
                "factors": ["Payment History", "Credit Utilization", "Length of Credit History", "Types of Credit"]
            },
            "cibil": {
                "definition": "TransUnion CIBIL is India's first credit information company",
                "score_range": "300-900",
                "importance": "Higher scores indicate better creditworthiness",
                "report_access": "You can check your CIBIL score once a year for free"
            },
            "credit report": {
                "definition": "A detailed breakdown of an individual's credit history",
                "contents": ["Personal Information", "Account History", "Credit Inquiries", "Public Records"],
                "importance": "Used by lenders to assess credit risk"
            },
            "emi": {
                "definition": "Equated Monthly Installment - fixed payment amount made by a borrower to a lender",
                "calculation": "EMI = [P × R × (1+R)^N]/[(1+R)^N-1], where P=Principal, R=Rate of interest, N=Tenure"
            }
        }
        
        self.wecredit_services = {
            "personal loan": {
                "interest_rate": "10.99% - 18.99%",
                "processing_fee": "1-2% of loan amount",
                "tenure": "12 - 60 months",
                "loan_amount": "₹50,000 - ₹10,00,000"
            },
            "home loan": {
                "interest_rate": "6.90% - 8.50%",
                "processing_fee": "0.5-1% of loan amount",
                "tenure": "5 - 30 years",
                "loan_amount": "Up to ₹5 crore"
            },
            "credit report": {
                "fee": "Free first report, ₹399 for additional reports",
                "delivery": "Digital delivery within 24 hours",
                "analysis": "Detailed analysis and improvement tips included"
            },
            "credit improvement": {
                "duration": "3-6 months program",
                "features": ["Personalized Plan", "Monthly Monitoring", "Expert Consultation"],
                "success_rate": "85% customers see improvement of 50+ points"
            }
        }
        
        self.faqs = {
            "how to apply for loan": "You can apply for a loan through our website or mobile app. Navigate to the 'Loans' section, select the type of loan, fill in your details, and submit required documents.",
            "how to check credit score": "You can check your credit score for free once a year through our 'Credit Health' section on the WeCredit app or website. We provide CIBIL scores along with a detailed analysis.",
            "loan rejection reasons": "Loan applications may be rejected due to low credit score, high existing debt, insufficient income, employment instability, or incomplete documentation.",
            "improve credit score": "You can improve your credit score by paying bills on time, reducing debt, avoiding multiple loan applications, maintaining old credit accounts, and regularly checking your credit report for errors."
        }


class ChatBot:
    def __init__(self):
        self.config = Config()
        self.knowledge = KnowledgeBase()
        openai.api_key = self.config.api_key
        
    def preprocess_query(self, query):
       
        query = query.lower().strip()
     
        query = re.sub(r'[^\w\s.,?]', '', query)
        return query
        
    def search_knowledge_base(self, query):
       
        for concept, info in self.knowledge.financial_concepts.items():
            if concept in query:
                return {
                    "type": "financial_concept",
                    "concept": concept,
                    "info": info
                }
        
      
        for service, details in self.knowledge.wecredit_services.items():
            if service in query:
                return {
                    "type": "service",
                    "service": service,
                    "details": details
                }
        
     
        for question, answer in self.knowledge.faqs.items():
            if self.is_similar(query, question):
                return {
                    "type": "faq",
                    "question": question,
                    "answer": answer
                }
        
        return None
    
    def is_similar(self, query, question):
   
        query_words = set(query.split())
        question_words = set(question.split())
        common_words = query_words.intersection(question_words)
    
        similarity = len(common_words) / len(question_words) if question_words else 0
        return similarity > 0.3
    
    def format_response(self, knowledge_item):
        if not knowledge_item:
            return None
            
        if knowledge_item["type"] == "financial_concept":
            concept = knowledge_item["concept"]
            info = knowledge_item["info"]
            response = f"{concept.title()}: {info['definition']}"
            
            if "types" in info:
                response += f"\n\nTypes: {', '.join(info['types'])}"
                
            if "calculation" in info:
                response += f"\n\nCalculation: {info['calculation']}"
                
            return response
            
        elif knowledge_item["type"] == "service":
            service = knowledge_item["service"]
            details = knowledge_item["details"]
            response = f"WeCredit {service.title()} Details:\n"
            
            for key, value in details.items():
                formatted_key = key.replace("_", " ").title()
                response += f"\n{formatted_key}: {value}"
                
            return response
            
        elif knowledge_item["type"] == "faq":
            return knowledge_item["answer"]
            
        return None
    
    def generate_llm_response(self, query, context=None):
        prompt = f"""You are WeCredit's financial assistant chatbot. Answer the following query related to financial services. 
        Be concise, helpful, and accurate.
        
        Query: {query}
        """
        
        if context:
            prompt += f"\n\nRelevant information: {context}"
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in LLM API call: {e}")
            return "I'm having trouble connecting to my knowledge base. Please try again later or contact customer support."
    
    def get_response(self, user_input):
        query = self.preprocess_query(user_input)
       
        knowledge_item = self.search_knowledge_base(query)
        structured_response = self.format_response(knowledge_item) if knowledge_item else None
        

        if structured_response:
            return structured_response
        
      
        return self.generate_llm_response(query)

    def log_conversation(self, user_input, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "user_input": user_input,
            "response": response
        }
        
        with open("conversation_logs.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")


def main():
    chatbot = ChatBot()
    print("WeCredit Financial Assistant")
    print("Type 'exit' to end the conversation\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Thank you for using WeCredit Financial Assistant. Have a great day!")
            break
            
        response = chatbot.get_response(user_input)
        print(f"\nWeCredit Assistant: {response}\n")
        chatbot.log_conversation(user_input, response)

if __name__ == "__main__":
    main()
