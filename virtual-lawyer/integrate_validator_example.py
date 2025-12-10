"""
Example: How to integrate Legal Accuracy Validator into your API
This shows the minimal changes needed to add validation
"""
from src.legal_accuracy_validator import LegalAccuracyValidator

# Initialize validator (do this once at startup)
validator = LegalAccuracyValidator()

# Example: Integration in api_complete.py chat endpoint
def chat_with_validation(question: str, use_formatter: bool = True):
    """
    Example of how to add validation to chat endpoint
    """
    # Your existing pipeline code
    # result = pipeline.generate_answer(question, use_formatter=use_formatter)
    
    # NEW: Validate the answer
    validation_result = validator.validate_answer(
        answer=result['answer'],
        question=question,
        references=result.get('references', [])
    )
    
    # Check if there are critical issues
    if not validation_result['valid']:
        print("⚠️ WARNING: Legal accuracy issues detected!")
        for issue in validation_result['issues']:
            print(f"  - {issue['message']}")
            if 'correction' in issue:
                print(f"    Correction: {issue['correction']}")
    
    # Add validation info to response
    result['validation'] = {
        'valid': validation_result['valid'],
        'score': validation_result['score'],
        'warnings': validation_result['warnings'],
        'recommendations': validation_result['recommendations']
    }
    
    # Optionally: Auto-correct if score is too low
    if validation_result['score'] < 50:
        print("⚠️ Answer has low accuracy score. Consider reviewing.")
        # You could trigger a retry or flag for manual review
    
    return result

# Example: Integration in two_stage_pipeline.py
def generate_answer_with_validation(self, question: str, use_formatter: bool = True):
    """
    Add validation to two-stage pipeline
    """
    # Existing pipeline code
    result = self.generate_answer(question, use_formatter)
    
    # NEW: Validate before returning
    validation = validator.validate_answer(
        answer=result['answer'],
        question=question,
        references=result.get('references', [])
    )
    
    # Log validation results
    if not validation['valid']:
        print(f"\n⚠️ Validation Issues Detected (Score: {validation['score']}/100):")
        for issue in validation['issues']:
            print(f"  [{issue['severity'].upper()}] {issue['message']}")
    
    # Add to result
    result['validation'] = validation
    
    return result

if __name__ == "__main__":
    # Test the validator
    test_question = "If all eyewitnesses support the prosecution but medical evidence contradicts the time of death, what is the rule of priority in Pakistani law?"
    test_answer = "Medical evidence has precedence over eyewitness testimony in Pakistani law."
    
    result = validator.validate_answer(test_answer, test_question)
    
    print("=" * 60)
    print("VALIDATION TEST")
    print("=" * 60)
    print(f"Valid: {result['valid']}")
    print(f"Score: {result['score']}/100")
    print(f"\nIssues Found: {len(result['issues'])}")
    for issue in result['issues']:
        print(f"\n  [{issue['severity']}] {issue['message']}")
        if 'correction' in issue:
            print(f"  Correction: {issue['correction']}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")






















