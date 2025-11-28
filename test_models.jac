# Test models
import models;

with entry {
    org = Organisation(name="Test", type="gov", contact_email="test@test.com");
    root ++> org;
    print("Models work");
}