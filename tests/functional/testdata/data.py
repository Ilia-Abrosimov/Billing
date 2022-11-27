from utils.models import Subscription, Payment

superadmin_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjE2ODcwOC1mMWMwLTQ3NjctOWI2ZC04NjAxZDM5NmZkOTEiLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MjAwMDAwMDAwMCwicm9sZXMiOlsiU3RhbmRhcnQiLCJzdXBlcmFkbWluIl19.J9jWWn93i-1e6MwhWYoTZ4rSOag7nnvdHDmePt00K4w'
user_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjE2ODcwOC1mMWMwLTQ3NjctOWI2ZC04NjAxZDM5NmZkOTEiLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MjAwMDAwMDAwMCwicm9sZXMiOlsiU3RhbmRhcnQiXX0.N-T5m3eFumq6pLTttwt9udwCYSMJegT8-lN7lC0cTjQ'

subscription = Subscription(
    title='subscription1',
    description='description',
    price=2000,
    roles=['basic']
)

payment = Payment(
    subscription='subscription1',
    start_date='2022-11-25',
)
