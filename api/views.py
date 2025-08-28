import os
from decimal import Decimal
from openai import OpenAI

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile, ChatSession, ChatMessage, GoldTransaction
from .serializers import GoldTransactionSerializer

# --- Chat API View ---

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatAPIView(APIView):
    """
    API endpoint for chatbot interactions.
    Manages chat sessions and integrates with OpenAI for responses.
    """
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        message_content = request.data.get('message')
        session_id = request.data.get('session_id')

        if not user_id or not message_content:
            return Response(
                {"error": "user_id and message are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Get or create the user profile
        user, _ = UserProfile.objects.get_or_create(user_id=user_id)

        # 2. Get or create the chat session
        try:
            if session_id:
                session = ChatSession.objects.get(session_id=session_id, user=user)
            else:
                # Create a new session and generate a title from the first message
                title = (message_content[:75] + '...') if len(message_content) > 75 else message_content
                session = ChatSession.objects.create(user=user, title=title)
        except ChatSession.DoesNotExist:
            return Response({"error": "Invalid session_id."}, status=status.HTTP_404_NOT_FOUND)

        # 3. Save the user's message
        ChatMessage.objects.create(session=session, role='user', content=message_content)

        # 4. Retrieve conversation history
        history = ChatMessage.objects.filter(session=session).order_by('timestamp')[:15]
        
        # Format messages for OpenAI API
        messages_for_api = [
            {"role": msg.role, "content": msg.content} for msg in history
        ]
        
        try:
            # 5. Send to OpenAI API
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini", # Or "gpt-4o", etc.
                    # messages=messages_for_api
                    messages=[
                        {"role": "system", "content": "You are a helpful history assistant."},
                        {"role": "user", "content": message_content}
                    ]
                )
                if completion and completion.choices and completion.choices[0].message:
                    ai_message = completion.choices[0].message.content
                else:
                    ai_message = "Sorry, I couldn't generate a response."
  
            except Exception as e:
                 ai_message = f"AI service failed: {str(e)}"            
                #  ai_response_content = completion.choices[0].message.content

            # 7. Save AI's response
            # ChatMessage.objects.create(session=session, role='assistant', content=ai_response_content)

            return Response({
                # "reply": ai_response_content,
                # "session_id": str(session.session_id)
                "session_id": str(session.session_id),
                "user_message": message_content,
                "ai_response": ai_message
            }, status=status.HTTP_200_OK)

        # except Exception as e:
        #     # Log the error for debugging
        #     print(f"Error calling OpenAI: {e}")
        #     return Response(
        #         {"error": "Failed to get a response from the AI service."},
        #         status=status.HTTP_503_SERVICE_UNAVAILABLE
        #     )
        except Exception as e:
            return Response(
                {"error": f"AI service failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- Gold Purchase API View ---

class GoldPurchaseAPIView(APIView):
    """
    API endpoint to emulate a gold purchase transaction.
    """
    # Hardcoded gold rate as per requirements
    GOLD_RATE_PER_GRAM = Decimal('75.50')

    def post(self, request, *args, **kwargs):
        user_name = request.data.get('user_name')
        weight_str = request.data.get('weight_in_grams')

        if not user_name or not weight_str:
            return Response(
                {"error": "user_name and weight_in_grams are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            weight_in_grams = Decimal(weight_str)
            if weight_in_grams <= 0:
                raise ValueError
        except (ValueError, TypeError):
             return Response(
                {"error": "weight_in_grams must be a positive number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Calculate total price
        total_price = self.GOLD_RATE_PER_GRAM * weight_in_grams
        
        # Prepare data for serializer
        transaction_data = {
            'user_name': user_name,
            'weight_in_grams': weight_in_grams,
            'gold_rate_per_gram_usd': self.GOLD_RATE_PER_GRAM,
            'total_price_usd': total_price
        }

        # 3. Create a new GoldTransaction record
        # Using a serializer for validation and creation
        try:
            serializer = GoldTransactionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
                response_data['status'] = 'Purchase successful'
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
