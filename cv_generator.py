# Initial file by Gemini
def generate_professional_cv(
    json_data,
    contact_name,
    contact_email,
    contact_phone,
    output_filename="my_cv.html",
    profile_extra_text="",
):
    """
    Parses a JSON object containing CV information and generates a
    professionally styled HTML CV.

    Args:
        json_data (dict): The CV data in dictionary format.
        contact_name (str): Full name of the contact for the "Wirokit contact" section.
        contact_email (str): Email address of the contact for the "Wirokit contact" section.
        contact_phone (str): Phone number of the contact for the "Wirokit contact" section.
        output_filename (str): The name of the file to create.
        profile_extra_text (str): Extra profile text to add as an additional paragraph.
    """

    # Get disclaimer text
    disclaimer = open(f"disclaimer.txt", "r").read()

    # Extract data with safe defaults using .get() to prevent errors if fields are missing
    name = json_data.get("name", "Name Not Provided")
    title = json_data.get("title", "")
    profile = json_data.get("profileText", "")
    highlight_skills = json_data.get("highlightSkills", [])
    raw_skills = json_data.get("skills", [])

    # Remove any skills already included in highlight_skills
    skills = filter(lambda skill: skill not in highlight_skills, raw_skills)

    # Handle Work Experience (Handling the specific single-object format provided)
    job_list = json_data.get("workExperience", [])

    # Handle Education
    edu_list = json_data.get("education", [])

    # Define CSS for a clean, professional look (Helvetica/Arial, clean lines)
    css_styles = """
    <style>
        @media print {
            div {
                break-inside: avoid;
                print-color-adjust: exact;
            }
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding-top: 0;
            color: #333;
            line-height: 1.6;
        }
        .confidential-header {
            text-align: center;
            margin: 0;
            color: rgb(220, 53, 69);
            position: absolute;
            top: 0;
            width: 100%;
        }
        .cv-container {
            max-width: 800px;
            margin: 0 auto;
            margin-top: 40px;
            background-color: #ffffff;
            padding: 50px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border-top: 5px solid #2c3e50;
        }

        /* Top Logo */
        .logo-container {
            margin-top: -40px;
            margin-bottom: -20px;
            display: flex;
            justify-content: center;
        }
        .top-logo {
            width: 150px;
        }

        /* Header Section */
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        header h1 {
            margin: 0;
            font-size: 2.5em;
            color: #2c3e50;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        header h2 {
            margin: 10px 0 0;
            font-size: 1.2em;
            color: #7f8c8d;
            font-weight: 400;
        }
        
        /* Section Styling */
        .section {
            margin-bottom: 40px;
        }
        .section-header {
            border-bottom: 2px solid #ecf0f1;
            margin-bottom: 20px;
            padding-bottom: 10px;
        }
        .section-header h3 {
            margin: 0;
            color: #2980b9;
            text-transform: uppercase;
            font-size: 1.1em;
            letter-spacing: 1px;
        }
        
        /* Content Styling */
        .skill-tag {
            display: inline-block;
            background-color: #e8f4f8;
            color: #2980b9;
            padding: 5px 12px;
            margin: 0 5px 5px 0;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: 600;
        }
        .hightlight {
            background-color: #3b82f6;
            color: white;
        }
        
        .entry {
            margin-bottom: 20px;
        }
        .entry-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            flex-wrap: wrap;
        }
        .entry-title {
            font-weight: bold;
            font-size: 1.1em;
            color: #2c3e50;
        }
        .entry-subtitle {
            font-style: italic;
            color: #7f8c8d;
        }
        .entry-date {
            font-size: 0.9em;
            color: #95a5a6;
        }
        .entry-description {
            margin-top: 8px;
        }
        .material-icons {
            vertical-align: middle;
            margin-top: -2.5px;
            color: rgb(34, 103, 150);
        }
    </style>
    """

    # Construct the HTML Content
    highlight_skills_html = "".join(
        [
            f'<span class="skill-tag hightlight">{skill}</span>'
            for skill in highlight_skills
        ]
    )

    skills_html = "".join(
        [f'<span class="skill-tag">{skill}</span>' for skill in skills]
    )

    skills_html_full = highlight_skills_html + skills_html

    job_html = "".join(
        map(
            lambda j: f"""
        <div class="entry">
            <div class="entry-header">
                <span class="entry-title">{j.get("title", "")}</span>
                <span class="entry-date">{j.get("timePeriod", "")}</span>
            </div>
            <div class="entry-subtitle">{j.get("company", "")}</div>
            <div class="entry-description">
                {j.get("description", "")}
            </div>
        </div>
    """,
            job_list,
        )
    )

    education_html = "".join(
        map(
            lambda e: f"""
        <div class="entry">
            <div class="entry-header">
                <span class="entry-title">{e.get("degree", "")}</span>
                <span class="entry-date">{e.get("timePeriod", "")}</span>
            </div>
            <div class="entry-subtitle">{e.get("school", "")}</div>
            <div class="entry-description">
                {e.get("description", "")}
            </div>
        </div>
    """,
            edu_list,
        )
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/x-icon" href="/static/images/favicon.ico" />
        <link
            rel="stylesheet"
            href="https://fonts.googleapis.com/icon?family=Material+Icons"
        />
        <title>{name} - CV</title>
        {css_styles}
    </head>
    <body>
        <h2 class="confidential-header">CONFIDENTIAL</h2>

        <div class="cv-container">
            <div class="logo-container">
                <img class="top-logo" src="/static/images/wirokit_b.png" />
            </div>

            <!-- Header -->
            <header>
                <h1>{name}</h1>
                <h2>{title}</h2>
            </header>

            <!-- Profile -->
            <div class="section">
                <div class="section-header">
                    <h3>Profile</h3>
                </div>
                <p>{profile}</p>
                {"" if profile_extra_text == "" else f"""
                    <p>{profile_extra_text}</p>
                """}
            </div>

            <!-- Skills -->
            <div class="section">
                <div class="section-header">
                    <h3>Skills</h3>
                </div>
                <div>{skills_html_full}</div>
            </div>

            <!-- Work Experience -->
            <div class="section">
                <div class="section-header">
                    <h3>Work Experience</h3>
                </div>
                {job_html}
            </div>

            <!-- Education -->
            {"" if len(edu_list) == 0 else f"""
                <div class="section">
                    <div class="section-header">
                        <h3>Education</h3>
                    </div>
                    {education_html}
                </div>
            """}

            <!-- Contact info -->
            <div class="section">
                <div class="section-header">
                    <h3>Wirokit contact</h3>
                </div>
                <div class="entry">
                    <div class="entry-header">
                        <span class="entry-title">{contact_name}</span>
                    </div>
                    <div class="entry-description">
                        <i class="material-icons">email</i> {contact_email}
                    </div>
                    <div class="entry-description">
                        <i class="material-icons">call</i> {contact_phone}
                    </div>
                    
                </div>
                <div class="entry">
                    <div class="entry-description">
                        {disclaimer}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Write to file
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully created CV: {output_filename}")
    except IOError as e:
        print(f"Error writing file: {e}")


# ---------------------------------------------------------
# Example Usage
# ---------------------------------------------------------
if __name__ == "__main__":
    # The example JSON data provided in the prompt
    raw_data = {
        "name": "John Doe",
        "title": "Professional actor",
        "profileText": "Experienced performer with a passion for dramatic arts and stage production.",
        "highlightSkills": ["Acrobatics", "Sleight of Hand", "Improvisation"],
        "skills": ["Voice Acting", "Stage Combat", "Improvisation", "Memorization"],
        "workExperience": [
            {
                "title": "Lead Actor",
                "company": "City Theater Company",
                "timePeriod": "1.10.2024 - 30.5.2025",
                "description": "Performed lead roles in three major productions. Coordinated with directors and costume designers.",
            },
            {
                "title": "Lead Actor",
                "company": "City Theater Company",
                "timePeriod": "1.10.2024 - 30.5.2025",
                "description": "Performed lead roles in three major productions. Coordinated with directors and costume designers.",
            },
        ],
        "education": [
            {
                "degree": "Bachelor of Arts in Acting",
                "school": "National Theater School",
                "timePeriod": "1.10.2020 - 30.5.2024",
                "description": "Specialized in Shakespearean drama and modern movement.",
            }
        ],
    }

    generate_professional_cv(
        raw_data, "Sampo Koski", "sales@wirokit.com", "+358 12 345 6789"
    )
