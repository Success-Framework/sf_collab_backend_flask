# Profile Management Implementation Guide

## ✅ What Has Been Implemented

### 1. **Database Schema Updates** (`app/models/user.py`)

Added the following fields to the User model:

```python
# Multi-Role Profile Fields
roles: JSON[]  # ["founder", "builder", "investor", "influencer"]
founder_profile: JSON  # Founder-specific data
builder_profile: JSON  # Builder-specific data
influencer_profile: JSON  # Influencer-specific data
investor_profile: JSON  # Investor-specific data

# Profile Completion Tracking
profile_setup_completed: Boolean  # Basic profile (ProfileSetup)
role_profile_completed: Boolean  # Multi-role profile (MultiRoleProfileForm)
```

### 2. **New Endpoints Created** (`app/routes/profile_routes.py`)

#### Endpoint 1: POST `/api/auth/setup-profile`
- **Purpose**: Basic profile setup (Step 1)
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `multipart/form-data` (supports file upload)
- **Fields**:
  - `firstName` (required)
  - `lastName` (required)
  - `company` (optional)
  - `country` (required)
  - `city` (optional)
  - `timezone` (optional, default: "UTC")
  - `language` (optional, default: "English")
  - `bio` (optional)
  - `profileImage` (optional, file - max 5MB, types: PNG, JPG, GIF, WebP)

**Response (200)**:
```json
{
  "success": true,
  "message": "Profile setup completed successfully",
  "data": { /* user object with updated profile */ }
}
```

**Response (422 - Validation Error)**:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "firstName": "First name is required",
    "country": "Country is required"
  }
}
```

---

#### Endpoint 2: POST `/api/users/complete-profile`
- **Purpose**: Multi-role profile completion (Step 2)
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "roles": ["founder", "builder"],
  "founderProfile": {
    "startupName": "String (required)",
    "description": "String (required)",
    "industry": "String (required)",
    "stage": "String (required) - idea|MVP|early revenue|scaling",
    "teamSize": "Number",
    "fundingRaised": "String",
    "fundingCurrency": "String",
    "website": "String",
    "lookingFor": ["Array of strings"],
    "coFoundersNeeded": "Number",
    "skillsNeeded": ["Array of strings"],
    "timeline": "String"
  },
  "builderProfile": {
    "skills": ["Array of strings (required, min 1)"],
    "experienceLevel": "String (required) - Junior|Mid-level|Senior|Lead|Principal",
    "availability": "String (required) - Full-time|Part-time|Occasional",
    "hourlyRate": "Number",
    "lookingFor": ["Array of strings"],
    "portfolio": "String (URL)",
    "timezone": "String",
    "bio": "String"
  },
  "influencerProfile": {
    "platforms": ["Array of strings (required, min 1)"],
    "xFollowers": "Number",
    "linkedinFollowers": "Number",
    "youtubeFollowers": "Number",
    "tiktokFollowers": "Number",
    "instagramFollowers": "Number",
    "newsletterSubscribers": "Number",
    "collabTypes": ["Array of strings (required, min 1)"],
    "audienceDescription": "String (required)",
    "industryFocus": ["Array of strings"],
    "mediaKit": "String (URL)",
    "bio": "String"
  },
  "investorProfile": {
    "investorType": "String (required) - Angel|VC|Syndicate|Scout",
    "aum": "String (Assets Under Management)",
    "industriesInvested": ["Array of strings (required, min 1)"],
    "checkSize": "String",
    "bio": "String",
    "website": "String"
  }
}
```

**Response (200)**:
```json
{
  "success": true,
  "message": "Multi-role profile saved successfully",
  "data": { /* user object with roles and all profile data */ }
}
```

**Response (422 - Validation Error)**:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "founderProfile": {
      "startupName": "Startup name is required",
      "description": "Description is required"
    }
  }
}
```

---

#### Endpoint 3: GET `/api/users/profile`
- **Purpose**: Retrieve user's complete profile
- **Authentication**: Required (Bearer Token)
- **Method**: GET
- **No Request Body**

**Response (200)**:
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "id": "integer",
    "firstName": "String",
    "lastName": "String",
    "email": "String",
    "roles": ["Array of role strings"],
    "profile": {
      "picture": "String (URL)",
      "bio": "String",
      "company": "String",
      "country": "String",
      "city": "String",
      "timezone": "String"
    },
    "founderProfile": { /* ... */ },
    "builderProfile": { /* ... */ },
    "influencerProfile": { /* ... */ },
    "investorProfile": { /* ... */ },
    "profileCompletion": {
      "basicProfileSetup": "Boolean",
      "roleProfileCompleted": "Boolean"
    },
    /* ... other user fields ... */
  }
}
```

---

#### Endpoint 4: PUT/PATCH `/api/users/profile`
- **Purpose**: Update user profile (partial updates allowed)
- **Authentication**: Required (Bearer Token)
- **Content-Type**: `application/json`
- **Request Body**: Any combination of fields from endpoints 1-2

**Response (200)**:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": { /* updated user object */ }
}
```

---

### 3. **Blueprint Registration**

The profile routes have been registered in `app/blueprints.py`:
```python
{ "blueprint": profile_routes.profile_bp, "url_prefix": ''},
```

This allows the endpoints to be accessed at:
- `POST http://localhost:5001/api/auth/setup-profile`
- `POST http://localhost:5001/api/users/complete-profile`
- `GET http://localhost:5001/api/users/profile`
- `PUT http://localhost:5001/api/users/profile`

---

### 4. **Validation**

#### Basic Profile Validation
- `firstName` - Required, non-empty
- `lastName` - Required, non-empty
- `country` - Required, non-empty

#### Role-Specific Validation

**Founder Profile**:
- `startupName` - Required
- `description` - Required
- `industry` - Required
- `stage` - Required

**Builder Profile**:
- `skills` - Required, at least 1 item
- `experienceLevel` - Required
- `availability` - Required

**Influencer Profile**:
- `platforms` - Required, at least 1 item
- `collabTypes` - Required, at least 1 item
- `audienceDescription` - Required

**Investor Profile**:
- `investorType` - Required
- `industriesInvested` - Required, at least 1 item

---

### 5. **User Model Serialization**

The `User.to_dict()` method now includes:
```python
'roles': user.roles or [],
'founderProfile': user.founder_profile or {},
'builderProfile': user.builder_profile or {},
'influencerProfile': user.influencer_profile or {},
'investorProfile': user.investor_profile or {},
'profileCompletion': {
    'basicProfileSetup': user.profile_setup_completed,
    'roleProfileCompleted': user.role_profile_completed
}
```

---

## 🧪 Testing Guide

### Prerequisites
```bash
# Ensure Docker is running
docker-compose -f docker/docker-compose-dev.yml up -d

# Ensure Flask backend is running
source .venv/bin/activate
python run.py
```

Backend will be available at: `http://localhost:5001`

### 1. Get Authentication Token

First, create a user and get a token:

```bash
# Signup
curl -X POST http://localhost:5001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "firstName": "John",
    "lastName": "Doe"
  }'

# Login to get token
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

Response will include `accessToken`. Save it as:
```bash
export TOKEN="your_access_token_here"
```

---

### 2. Test Setup Profile Endpoint

**With text fields only**:
```bash
curl -X POST http://localhost:5001/api/auth/setup-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "firstName=John" \
  -F "lastName=Doe" \
  -F "country=United States" \
  -F "company=Acme Labs" \
  -F "city=San Francisco" \
  -F "timezone=PST (UTC-8)" \
  -F "language=English" \
  -F "bio=Building the future"
```

**With image upload**:
```bash
curl -X POST http://localhost:5001/api/auth/setup-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "firstName=John" \
  -F "lastName=Doe" \
  -F "country=United States" \
  -F "profileImage=@/path/to/profile_pic.jpg"
```

**Expected Response (200)**:
```json
{
  "success": true,
  "message": "Profile setup completed successfully",
  "data": {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "test@example.com",
    "profile": {
      "picture": "/uploads/user_avatars/profile_1_...",
      "company": "Acme Labs",
      "country": "United States",
      "city": "San Francisco",
      "timezone": "PST (UTC-8)"
    },
    "profileCompletion": {
      "basicProfileSetup": true,
      "roleProfileCompleted": false
    }
  }
}
```

---

### 3. Test Complete Profile Endpoint

```bash
curl -X POST http://localhost:5001/api/users/complete-profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["founder", "builder"],
    "founderProfile": {
      "startupName": "Acme Labs",
      "description": "AI-powered automation platform",
      "industry": "AI / ML",
      "stage": "MVP",
      "teamSize": 3,
      "fundingRaised": "500000",
      "fundingCurrency": "USD",
      "website": "https://acme.com",
      "lookingFor": ["contributors", "investors"],
      "coFoundersNeeded": 1,
      "skillsNeeded": ["Frontend", "Backend"],
      "timeline": "6 months"
    },
    "builderProfile": {
      "skills": ["Frontend", "Backend", "DevOps"],
      "experienceLevel": "Senior",
      "availability": "Full-time",
      "hourlyRate": 150,
      "lookingFor": ["Paid", "Equity"],
      "portfolio": "https://portfolio.com",
      "timezone": "PST (UTC-8)",
      "bio": "10 years of experience in web development"
    }
  }'
```

**Expected Response (200)**:
```json
{
  "success": true,
  "message": "Multi-role profile saved successfully",
  "data": {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "test@example.com",
    "roles": ["founder", "builder"],
    "founderProfile": { /* ... */ },
    "builderProfile": { /* ... */ },
    "profileCompletion": {
      "basicProfileSetup": true,
      "roleProfileCompleted": true
    }
  }
}
```

---

### 4. Test Get Profile Endpoint

```bash
curl -X GET http://localhost:5001/api/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200)**:
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "test@example.com",
    "roles": ["founder", "builder"],
    "profile": { /* ... */ },
    "founderProfile": { /* ... */ },
    "builderProfile": { /* ... */ },
    "profileCompletion": {
      "basicProfileSetup": true,
      "roleProfileCompleted": true
    }
  }
}
```

---

### 5. Test Validation Errors

**Missing required field**:
```bash
curl -X POST http://localhost:5001/api/auth/setup-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "firstName=John"
  # Missing: lastName, country
```

**Expected Response (422)**:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "lastName": "Last name is required",
    "country": "Country is required"
  }
}
```

**Invalid role in complete-profile**:
```bash
curl -X POST http://localhost:5001/api/users/complete-profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["invalid_role"]
  }'
```

**Expected Response (422)**:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "roles": "Invalid roles: invalid_role"
  }
}
```

---

### 6. Test File Upload Validation

**File too large**:
```bash
# Create a 10MB file
dd if=/dev/zero of=large_file.jpg bs=1M count=10

curl -X POST http://localhost:5001/api/auth/setup-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "firstName=John" \
  -F "lastName=Doe" \
  -F "country=US" \
  -F "profileImage=@large_file.jpg"
```

**Expected Response (413)**:
```json
{
  "success": false,
  "message": "File size exceeds 5MB limit"
}
```

**Invalid file type**:
```bash
curl -X POST http://localhost:5001/api/auth/setup-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "firstName=John" \
  -F "lastName=Doe" \
  -F "country=US" \
  -F "profileImage=@document.pdf"
```

**Expected Response (400)**:
```json
{
  "success": false,
  "message": "Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WebP"
}
```

---

### 7. Test Update Profile Endpoint

```bash
curl -X PUT http://localhost:5001/api/users/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Updated bio",
    "roles": ["founder", "builder", "investor"]
  }'
```

**Expected Response (200)**:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "profile": {
      "bio": "Updated bio"
    },
    "roles": ["founder", "builder", "investor"]
  }
}
```

---

## 🚀 Frontend Integration

The frontend can now:

1. **Call `/api/auth/setup-profile`** after sign-up to capture basic profile
2. **Call `/api/users/complete-profile`** to save multi-role data
3. **Call `/api/users/profile`** to fetch and display user profile with roles
4. **Display role badges** based on the `roles` array returned

---

## 📋 Database Migrations (If Using Alembic)

If you're using Alembic for migrations, run:

```bash
# Generate migration
alembic revision --autogenerate -m "Add multi-role profile fields to User model"

# Apply migration
alembic upgrade head
```

---

## 🔍 Troubleshooting

### Issue: "No such table: user" when running endpoints
**Solution**: Run database migrations or ensure database is initialized:
```bash
python run.py  # This should initialize DB on first run
```

### Issue: "Module 'profile_routes' not found"
**Solution**: Ensure the file is saved and restart the Flask server:
```bash
pkill -f "python run.py"
source .venv/bin/activate
python run.py
```

### Issue: "Validation failed" on valid data
**Solution**: Double-check field names match exactly (camelCase)

### Issue: Image upload not working
**Solution**: Ensure `uploads/user_avatars/` directory exists:
```bash
mkdir -p uploads/user_avatars
```

---

## 📊 Next Steps

1. **Deploy to production** - Update environment variables for cloud storage
2. **Add profile image cloud storage** - Use AWS S3, Cloudinary, or similar
3. **Add search indexes** - Create database indexes for role queries
4. **Add audit logging** - Log profile updates for security
5. **Add rate limiting** - Protect endpoints from abuse
6. **Frontend display** - Implement role badges on profile page

---

## 📝 Summary

✅ User model extended with role fields
✅ 4 new API endpoints created
✅ Comprehensive validation per role
✅ File upload support (image)
✅ Profile completion tracking
✅ Full error handling with detailed messages

All endpoints are ready for frontend integration!
