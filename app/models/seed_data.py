from app import db
from app.models.memorial import Memorial
from app.models.photo import Photo
from app.models.tribute import Tribute
from app.models.user import User
from app.models.theme import Theme
from datetime import datetime
import os
import shutil
from PIL import Image
import requests
from io import BytesIO

def generate_profile_photo(name, save_path):
    """Generate a profile photo using DiceBear API"""
    try:
        url = f"https://api.dicebear.com/7.x/initials/png?seed={name}&size=400"
        print(f"Generating profile from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Saved profile photo to: {save_path}")
        return os.path.basename(save_path)
    except Exception as e:
        print(f"Error generating profile photo: {str(e)}")
        raise

def download_photo(url, save_path):
    """Download photo from URL and save it"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Print response info for debugging
        print(f"Downloading {url}")
        print(f"Response status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        
        # Save the raw content directly to file
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return os.path.basename(save_path)
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        # Return a default image or raise the error
        raise

def seed_data():
    print("Seeding example data...")
    
    # Ensure upload directory exists with proper permissions
    base_upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    os.makedirs(base_upload_dir, exist_ok=True)
    print(f"Upload directory: {base_upload_dir}")

    # Create example user if not exists
    user = User.query.filter_by(email="example@example.com").first()
    if not user:
        user = User(
            username="ExampleUser",
            email="example@example.com"
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Example memorials data
    memorials_data = [
        {
            "name": "Eleanor Roosevelt",
            "birth_date": datetime(1884, 10, 11),
            "death_date": datetime(1962, 11, 7),
            "biography": """Eleanor Roosevelt was an American political figure, diplomat, and activist. She served as the First Lady of the United States from 1933 to 1945, making her the longest-serving First Lady in history.

She was a champion of civil rights, women's rights, and social justice. Her work with the United Nations earned her the nickname "First Lady of the World."

Eleanor revolutionized the role of First Lady, holding press conferences, giving lectures, and writing a daily newspaper column.""",
            "photos": [
                {
                    "filename": "profile_eleanor.png",
                    "is_profile": True,
                    "caption": "Portrait of Eleanor Roosevelt",
                    "url": None
                },
                {
                    "filename": "eleanor_un.jpg",
                    "is_profile": False,
                    "caption": "Eleanor Roosevelt at the United Nations, 1947",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Eleanor_Roosevelt_portrait_1933.jpg/800px-Eleanor_Roosevelt_portrait_1933.jpg"
                },
                {
                    "filename": "eleanor_fdr.jpg",
                    "is_profile": False,
                    "caption": "With President Franklin D. Roosevelt",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Eleanor_Roosevelt_portrait_1933.jpg/800px-Eleanor_Roosevelt_portrait_1933.jpg"
                }
            ],
            "tributes": [
                "A true pioneer for human rights and dignity for all.",
                "Her work with the UN helped shape the modern world.",
                "An inspiration to generations of women in politics."
            ]
        },
        {
            "name": "Albert Einstein",
            "birth_date": datetime(1879, 3, 14),
            "death_date": datetime(1955, 4, 18),
            "biography": """Albert Einstein was a theoretical physicist who developed the theory of relativity, one of the two pillars of modern physics. His work is also known for its influence on the philosophy of science.

Best known to the general public for his mass–energy equivalence formula E = mc². He received the 1921 Nobel Prize in Physics for his services to theoretical physics.

Einstein published more than 300 scientific papers and more than 150 non-scientific works.""",
            "photos": [
                {
                    "filename": "profile_albert.png",
                    "is_profile": True,
                    "caption": "Portrait of Albert Einstein",
                    "url": None
                },
                {
                    "filename": "einstein_chalk.jpg",
                    "is_profile": False,
                    "caption": "Einstein at Princeton, 1947",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1947.jpg/800px-Einstein_1947.jpg"
                },
                {
                    "filename": "einstein_office.jpg",
                    "is_profile": False,
                    "caption": "In his study at Princeton",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Einstein_1931_Columbia.jpg/800px-Einstein_1931_Columbia.jpg"
                }
            ],
            "tributes": [
                "His theories changed our understanding of the universe.",
                "Not just a brilliant mind, but a humanitarian at heart.",
                "His work continues to inspire scientists today."
            ]
        },
        {
            "name": "Maya Angelou",
            "birth_date": datetime(1928, 4, 4),
            "death_date": datetime(2014, 5, 28),
            "biography": """Maya Angelou was an American poet, memoirist, and civil rights activist. She published seven autobiographies, three books of essays, several books of poetry, and is credited with a list of plays, movies, and television shows.

She received dozens of awards and more than 50 honorary degrees. Angelou is best known for her series of seven autobiographies, which focus on her childhood and early adult experiences.

Her books center on themes such as racism, identity, family and travel.""",
            "photos": [
                {
                    "filename": "profile_maya.png",
                    "is_profile": True,
                    "caption": "Portrait of Maya Angelou",
                    "url": None
                },
                {
                    "filename": "maya_reading.jpg",
                    "is_profile": False,
                    "caption": "Maya Angelou in 1970",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Maya_Angelou_1970.jpg/800px-Maya_Angelou_1970.jpg"
                },
                {
                    "filename": "maya_speaking.jpg",
                    "is_profile": False,
                    "caption": "At Clinton's Inauguration, 1993",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Maya_Angelou_2011.jpg/800px-Maya_Angelou_2011.jpg"
                }
            ],
            "tributes": [
                "Her words gave voice to generations.",
                "A phenomenal woman who inspired millions.",
                "Her legacy lives on through her powerful works."
            ]
        }
    ]

    # Create memorials
    for memorial_data in memorials_data:
        # Check if memorial already exists
        if not Memorial.query.filter_by(name=memorial_data["name"]).first():
            memorial = Memorial(
                name=memorial_data["name"],
                birth_date=memorial_data["birth_date"],
                death_date=memorial_data["death_date"],
                biography=memorial_data["biography"],
                creator_id=user.id,
                is_public=True,
                theme_id=Theme.query.filter_by(name="Classic").first().id
            )
            db.session.add(memorial)
            db.session.commit()

            # Create memorial-specific upload directory
            upload_dir = os.path.join(base_upload_dir, str(memorial.id))
            os.makedirs(upload_dir, exist_ok=True)
            print(f"Created directory for memorial {memorial.id}: {upload_dir}")

            # Add all photos
            for photo_data in memorial_data["photos"]:
                file_path = os.path.join(upload_dir, photo_data["filename"])
                
                try:
                    if photo_data["is_profile"]:
                        # Generate profile photo using DiceBear
                        print(f"Generating profile photo for {memorial_data['name']}")
                        filename = generate_profile_photo(memorial_data["name"], file_path)
                    else:
                        # Download historical photo
                        print(f"Downloading photo: {photo_data['url']}")
                        filename = download_photo(photo_data["url"], file_path)

                    # Verify file exists and has content
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"Saved {filename} ({file_size} bytes)")
                    else:
                        print(f"Error: File not created: {file_path}")

                    photo = Photo(
                        filename=filename,
                        memorial_id=memorial.id,
                        is_profile=photo_data["is_profile"],
                        caption=photo_data["caption"]
                    )
                    db.session.add(photo)
                    print(f"Added photo record to database: {filename}")

                except Exception as e:
                    print(f"Error processing photo {photo_data['filename']}: {str(e)}")
                    continue

            # Add tributes
            for tribute_text in memorial_data["tributes"]:
                tribute = Tribute(
                    content=tribute_text,
                    author_id=user.id,
                    memorial_id=memorial.id,
                    is_approved=True
                )
                db.session.add(tribute)

            db.session.commit()
            print(f"Created memorial for {memorial_data['name']}")

    print("Seeding completed successfully") 