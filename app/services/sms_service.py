# import os
# import random
# from twilio.rest import Client
# from datetime import datetime, timedelta
# import requests
# # # curl -X POST https://api.sendmator.com/v1/sms/send \
# #   -H "X-API-Key: YOUR_API_KEY" \
# #   -H "Content-Type: application/json" \
# #   -d '{
# #         "recipient_type": "contact",
# #         "contact_external_id": "user_1234",
# #         "content": "Hello from Python!"
# #       }'
# class SMSService:
#     def __init__(self):
#         self.sendmator_api_key = os.getenv("SENDMATOR_API_KEY")
#         self.env = os.getenv("FLASK_ENV", "development")
#         self.api_url = "https://api.sendmator.com/v1/sms/send"
#         if not self.sendmator_api_key:
#             raise ValueError("Sendmator API key not configured")
#     # -------------------------
#     # Core sender
#     # -------------------------
#     def send_sms(self, phone_number: str, message: str) -> bool:
#         if self.env != "production":
#             print(f"[SMS MOCK] {phone_number}: {message}")
#             return True

#         try:
#             response = requests.post(self.api_url,
#                 headers={
#                     "X-API-Key": self.sendmator_api_key,
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "recipient_type": "direct_sms",
#                     "phone_number": phone_number,
#                     "content": message
#                 }
#             )
#             response.raise_for_status()
#             return True
#         except Exception as e:
#             print(f"[SMS ERROR] {e}")
#             return False

#     # -------------------------
#     # OTP / Verification
#     # -------------------------
#     def send_verification_code(self, phone_number: str) -> tuple[str, datetime]:
#         code = self._generate_code()
#         expires_at = datetime.utcnow() + timedelta(minutes=5)

#         message = f"Your verification code is {code}. It expires in 5 minutes."

#         self.send_sms(phone_number, message)
#         return code, expires_at

#     # -------------------------
#     # Helpers
#     # -------------------------
#     def _generate_code(self, length: int = 6) -> str:
#         return "".join(random.choices("0123456789", k=length))

#     def _normalize_phone(self, phone_number: str) -> str:
#         phone = phone_number.strip()
#         if not phone.startswith("+"):
#             raise ValueError("Phone number must be in E.164 format")
#         return phone

# def _test_sms_service():
#     sms_service = SMSService()
#     test_number = '+573024690359'
#     if not test_number:
#         print("Set TEST_PHONE_NUMBER in environment to run SMS test.")
#         return

#     code, expires_at = sms_service.send_verification_code(test_number)
#     print(f"Sent code {code} to {test_number}, expires at {expires_at}")
# # import requests
# # def send_sms():
# #     response = requests.post('https://textbelt.com/text', data={
# #       'phone': '573024690359',
# #       'message': 'Hello world',
# #       'key': 'textbelt',
# #     })
# # send_sms()
# # _test_sms_service()