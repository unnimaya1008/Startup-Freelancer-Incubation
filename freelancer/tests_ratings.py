from django.test import TestCase
from accounts.models import CustomUser
from startup.models import StartupProfile
from freelancer.models import FreelancerProfile, FreelancerRating
from projects.models import Project


class FreelancerRatingTests(TestCase):
    def setUp(self):
        self.startup_user = CustomUser.objects.create_user(username="startup", role="STARTUP")
        self.startup_profile = StartupProfile.objects.create(user=self.startup_user, startup_name="Startup Inc")
        
        self.freelancer_user = CustomUser.objects.create_user(username="freelancer", role="FREELANCER")
        self.freelancer_profile = FreelancerProfile.objects.create(user=self.freelancer_user, full_name="John Doe")
        
        self.project = Project.objects.create(
            startup=self.startup_profile, 
            name="Test Project", 
            status="COMPLETED",
            start_date="2024-01-01"
        )

    def test_average_rating_calculation(self):
        # Create first rating
        FreelancerRating.objects.create(
            freelancer=self.freelancer_profile,
            startup=self.startup_profile,
            project=self.project,
            timeliness_rating=5,
            quality_rating=4,
            communication_rating=3,
            feedback="Good job"
        )
        
        # Create second rating for a different project
        project2 = Project.objects.create(
            startup=self.startup_profile, 
            name="Project 2", 
            status="COMPLETED",
            start_date="2024-02-01"
        )
        FreelancerRating.objects.create(
            freelancer=self.freelancer_profile,
            startup=self.startup_profile,
            project=project2,
            timeliness_rating=3,
            quality_rating=4,
            communication_rating=5,
            feedback="Excellent communication"
        )
        
        ratings = self.freelancer_profile.get_average_ratings
        
        # (5+3)/2 = 4.0
        self.assertEqual(ratings['timeliness'], 4.0)
        # (4+4)/2 = 4.0
        self.assertEqual(ratings['quality'], 4.0)
        # (3+5)/2 = 4.0
        self.assertEqual(ratings['communication'], 4.0)
        # (4+4+4)/3 = 4.0
        self.assertEqual(ratings['overall'], 4.0)
        self.assertEqual(ratings['count'], 2)

    def test_one_rating_per_project_enforcement(self):
        FreelancerRating.objects.create(
            freelancer=self.freelancer_profile,
            startup=self.startup_profile,
            project=self.project,
            timeliness_rating=5,
            quality_rating=5,
            communication_rating=5
        )
        
        with self.assertRaises(Exception):
            FreelancerRating.objects.create(
                freelancer=self.freelancer_profile,
                startup=self.startup_profile,
                project=self.project,
                timeliness_rating=1,
                quality_rating=1,
                communication_rating=1
            )
