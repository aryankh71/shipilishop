from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from apps.account.models import CustomerProfile


User = get_user_model()


class CustomerProfileModelTest(TestCase):


    def setUp(self):

        self.user = User.objects.create_user(

            username="ali",

            email="ali@test.com",

            password="123456",

            phone_number="09123456789",

            role=User.Role.CUSTOMER

        )


    def test_customer_profile_creation(self):

        profile = CustomerProfile.objects.create(

            user=self.user,

            first_name="Ali",

            last_name="Khodakhah",

            national_code="1234567890"

        )


        self.assertEqual(
            profile.user,
            self.user
        )


        self.assertEqual(
            profile.first_name,
            "Ali"
        )


        self.assertEqual(
            profile.last_name,
            "Khodakhah"
        )


        self.assertEqual(
            profile.national_code,
            "1234567890"
        )



    def test_profile_string_method(self):

        profile = CustomerProfile.objects.create(

            user=self.user,

            first_name="Ali",

            last_name="Khodakhah"

        )


        self.assertEqual(

            str(profile),

            "Ali Khodakhah"

        )



    def test_profile_one_to_one_relation(self):


        CustomerProfile.objects.create(

            user=self.user,

            first_name="Ali"

        )


        with self.assertRaises(IntegrityError):

            CustomerProfile.objects.create(

                user=self.user,

                first_name="Another"

            )



    def test_profile_optional_fields_can_be_empty(self):


        profile = CustomerProfile.objects.create(

            user=self.user

        )


        self.assertEqual(

            profile.first_name,

            ""

        )


        self.assertEqual(

            profile.last_name,

            ""

        )


        self.assertIsNone(

            profile.national_code

        )



    def test_profile_avatar_upload(self):


        image = SimpleUploadedFile(

            name="avatar.jpg",

            content=b"fake image",

            content_type="image/jpeg"

        )


        profile = CustomerProfile.objects.create(

            user=self.user,

            avatar=image

        )


        self.assertIn(

            "profile/avatar",

            profile.avatar.name

        )



    def test_unique_national_code(self):


        CustomerProfile.objects.create(

            user=self.user,

            national_code="1234567890"

        )


        second_user = User.objects.create_user(

            username="reza",

            email="reza@test.com",

            password="123456",

            phone_number="09111111111"

        )


        with self.assertRaises(IntegrityError):

            CustomerProfile.objects.create(

                user=second_user,

                national_code="1234567890"

            )