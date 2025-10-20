import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	ScrapeWebsiteTool,
	FileReadTool
)






@CrewBase
class ExpertSChatbotEmpireBuilderRoiNicheHybridIntegrationCrew:
    """ExpertSChatbotEmpireBuilderRoiNicheHybridIntegration crew"""

    
    @agent
    def roi_focused_strategy_analyst(self) -> Agent:

        
        return Agent(
            config=self.agents_config["roi_focused_strategy_analyst"],
            
            
            tools=[
				ScrapeWebsiteTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def deep_integration_developer(self) -> Agent:

        
        return Agent(
            config=self.agents_config["deep_integration_developer"],
            
            
            tools=[
				FileReadTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def hybrid_pricing_model_expert(self) -> Agent:

        
        return Agent(
            config=self.agents_config["hybrid_pricing_model_expert"],
            
            
            tools=[

            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def high_value_niche_specialist(self) -> Agent:

        
        return Agent(
            config=self.agents_config["high_value_niche_specialist"],
            
            
            tools=[
				ScrapeWebsiteTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def calculate_roi_and_cost_savings_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["calculate_roi_and_cost_savings_analysis"],
            markdown=False,
            
            
        )
    
    @task
    def identify_high_value_niche_specialization(self) -> Task:
        return Task(
            config=self.tasks_config["identify_high_value_niche_specialization"],
            markdown=False,
            
            
        )
    
    @task
    def build_deep_integration_chatbot_solution(self) -> Task:
        return Task(
            config=self.tasks_config["build_deep_integration_chatbot_solution"],
            markdown=False,
            
            
        )
    
    @task
    def create_hybrid_pricing_business_model(self) -> Task:
        return Task(
            config=self.tasks_config["create_hybrid_pricing_business_model"],
            markdown=False,
            
            
        )
    
    @task
    def final_strategic_recommendation(self) -> Task:
        return Task(
            config=self.tasks_config["final_strategic_recommendation"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the ExpertSChatbotEmpireBuilderRoiNicheHybridIntegration crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
