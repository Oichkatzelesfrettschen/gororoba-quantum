# Competitions Setup

# Overview

Anybody can launch a machine learning competition using Kaggle's Community Competitions platform, including educators, researchers, companies, meetup groups, hackathon hosts, or inquisitive individuals! In this guide, you will learn how to set up your own competition, step-by-step. Before diving in, it's helpful to understand how each of our competition types work, to better understand what format is best for you:

## Types of Kaggle Competitions

You can create multiple competition types on Kaggle:

- **Prediction Competitions** are supervised machine learning competitions with a dataset, a problem statement, and a known answer key. Participant submissions are scored automatically through an evaluation metric, and a live leaderboard reflects results. Participants will download the data, build models on it locally or in Kaggle Notebooks, generate a prediction file, then upload predictions as a submission on Kaggle. In a classroom setting, these could be considered your “math tests.”
- **Hackathon Competitions** may ask a variety of data tasks, like building an app, exploring a dataset, creatively testing out a product, or producing educational content. These competitions do not need to have a dataset or an answer key, but do require a panel of judges prepared to review submissions and establish winners. In a classroom setting, these could be considered your “term papers.”

As a guide, prediction competitions are best if you’re looking to explore the depth of a problem space (e.g. accuracy), and hackathons are best if you’re looking to explore the width of a problem space (e.g. creativity). Once you’ve determined which competition format is best for you, see below to help get started.

***

### Prediction Competitions

A prediction competition has two things:

- A clearly defined problem that participants need to solve using a machine learning model.
- A dataset that’s used both for training and evaluating the effectiveness of these models.

For example, in the Store Sales – Time Series Forecasting competition, participants must accurately predict sales using a dataset of past product information. Once the competition starts, participants submit predictions, Kaggle scores them, and the team at the top of the leaderboard at the deadline wins!

#### Datasets, Submissions & Leaderboards

Every competition’s dataset is split into two smaller datasets:

- **train.csv:** Given to participants to train their models.
- **test.csv & solution.csv:** test.csv contains feature values for participants to make predictions. solution.csv contains the ground truth and is never shown to participants.

**Public vs. Private Leaderboards:**

To prevent overfitting, the solution.csv is split into two parts:

- **Public Leaderboard:** Visible during the competition to provide feedback.
- **Private Leaderboard:** Kept secret until the deadline. This is the official leaderboard used to determine the final ranking.

#### Create your Competition

Click the "Create new competition" button at the top of the Kaggle Community landing page. Select “Machine Learning Competition”

#### Visibility & Access

- **Public:** Viewable on Kaggle and in search results.
- **Private:** Hidden; only accessible via an invitation URL.

#### Who Can Join

- **Anyone:** Open to all Kagglers.
- **Only people with a link:** Restricted to those with the specific URL.
- **Restricted email list:** Most private; matches specific domains/emails. Note: Notebooks are disabled by default here to prevent data leaks.

#### Offering Prizes

Community hosts can offer prizes up to $25,000 USD in value.

- **Enable Prizes:** Select "Competition will award prizes" during creation.
- **Documentation:** You must specify prize counts and criteria in the Rules and Overview sections.
- **Fulfillment:** Hosts are solely responsible for distributing prizes and complying with tax rules. Kaggle does not facilitate prize distribution for Community Competitions.

#### Prepare the Dataset

You will typically need four CSV files:

- **train.csv:** Training data (Inputs + Ground Truth). ~70% of data.
- **test.csv:** Test features for participants (Inputs only).
- **solution.csv:** Hidden ground truth for Kaggle to score submissions.
- **sample\_submission.csv:** A template showing the required format.

#### Requirements

- **Unique ID Column:** Ensure your dataset has an Id column as the first column so the system can map predictions to solutions.
- **Usage Column:** In solution.csv, add a column named Usage with values: Public, Private, or Ignored.

#### Example File Formats

**train.csv**

```
input_feature1,input_feature2,target_feature
100,52.12,1
192,203.2,1
```

**solution.csv**

```
id,target_feature,Usage
0,1,Public
1,0,Private
2,1,Ignored
```

#### Set Up Scoring

Navigate to Host &gt; Evaluation Metric to configure how submissions are ranked.

#### Metrics

- **Legacy Metrics:** Older system with limited documentation; requires manual column mapping.
- **Custom Python Metrics:** Modern metrics with public source code and documentation.

#### Uploading Files

- Upload solution.csv.
- Upload sample\_submission.csv.
- Map the columns (required for Legacy metrics).
- **Upload Data for Participants:** Use the Data tab to upload the public files (train.csv, test.csv, etc.).

#### Creating a New Metric

You can implement custom metrics in a Python notebook.

- **Function Signature:** Must accept solution, submission, and row\_id\_column\_name.
- **Type Annotations:** All arguments and return values must be annotated.
- **Errors:** Use ParticipantVisibleError if you want the user to see the error details.
- **Constraints:** 30-minute runtime limit; no internet access allowed during scoring.

#### Test Your Competition

- **Sandbox Testing:** Test your own submissions before launching. Ensure a perfect submission yields a perfect score.
- **Benchmarking:** You can designate a specific submission as a "Benchmark" to show as a baseline on the leaderboard.

#### Finalize & Launch

- **Basic Details:** Upload images and set the "Score Decimals to Display" (truncating decimals can prevent "leaderboard probing").
- **Launch Checklist:** Once all boxes are green, you can launch immediately or schedule it for the future.
- **Inviting:** Share the unique URL found in the Launch Checklist.

#### FAQs

- **Where to get data?** Source your own private data to prevent cheating, or use public datasets with appropriate licenses.
- **Can I rescore?** You can upload a new solution file, but you must contact Kaggle Support to trigger a full rescore of an active competition.
- **Support:** Kaggle does not provide hands-on support for Community Competitions. Use the Competition Hosting Forum for peer help.
- **Participant Emails:** For privacy reasons, hosts cannot download participant email addresses.

***

### Hackathon Competitions

A Hackathon Competition requires three things:

- A clearly defined problem that participants need to address
- An evaluation rubric that’s used to judge the quality of each submission
- A panel of judges prepared to review the submissions from the competition and declare a winner

While supervised machine learning competitions (i.e. “Prediction competitions”) require a dataset, ground truth (answer key) that is both known and private, and an evaluation metric, a Hackathon allows users to build creative, diverse solutions to more open-ended, subjective challenges. If a Prediction competition is similar to a math test, then a Hackathon is similar to a term paper.

A few example Hackathons include:

- **[Gemma 3n Impact Challenge](https://www.kaggle.com/competitions/google-gemma-3n-hackathon)** - build your best products for a better world using the latest Gemma model
- **[OpenAI to Z Challenge](https://www.kaggle.com/competitions/openai-to-z-challenge)**- Use OpenAI o3/o4 mini and GPT 4.1 models to help identify possibly hidden archeological sites
- **[Vibe Code with Gemini 3 Pro in AI Studio](https://www.kaggle.com/competitions/gemini-3)o** - Build with Gemini 3 and compete for $500,000 in credits
- **[NFL Big Data Bowl](https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics)** - Understand player movement while the ball is in the air

#### Craft a Focused Problem Statement

It’s important to keep the focus of your Kaggle Hackathon narrow. Take time with your team to focus on why you want to run a Hackathon. While it may be tempting to expand the scope of your Hackathon to invite a broad range of ideas, a more focused project will give you better submissions because:

- **Clear Expectations:** A narrow focus provides participants with clear expectations and direction. They understand the specific problem they need to solve, which reduces confusion and allows them to concentrate their efforts effectively.
- **Measurable Outcomes:** Specificity enables easier and more objective evaluation. When the scope is limited, judging criteria can be more precise, leading to fairer and more transparent results.
- **Engaged Participants:** Specific problems often attract participants with specialized skills and interests. This leads to a more engaged and motivated community, fostering a more productive and innovative competition environment.
- **Effective Judging:** With a narrow scope, judges can represent expertise in the specific area, allowing for more informed and efficient evaluation of submissions. It also reduces the burden on judges who would otherwise have to assess a wide range of diverse and potentially unrelated solutions.

A few examples of how to narrow your problem statement:

| ❌ Instead of | ✅ Try this: |
| --- | --- |
| “Make a fun app.” | “Use Gemini to make a one-prompt 3D mobile game for iOS or Android.” |
| “Create an educational Youtube video on computing” | “Create an educational Youtube video designed to teach career switchers how to make a web application with a focus on Javascript” |
| “Uncover interesting insights from this dataset” | “Develop a new metric to better understand player safety, using this provided basketball dataset.” |

#### Create Your Competition

Click the "Create new competition" button at the top of the Kaggle Community landing page. Select “Hackathon”.

#### Visibility & Access

- **Public:** Viewable on Kaggle and in search results.
- **Private:** Hidden; only accessible via an invitation URL.

##### Who Can Join:

- **Anyone:** Open to all Kagglers.
- **Only people with a link:** Restricted to those with the specific URL.
- **Restricted email list:** Most private; matches specific domains/emails. Note: Notebooks are disabled by default here to prevent data leaks.

#### Offering Prizes

Community hosts can offer prizes up to $25,000 USD in value.

- **Enable Prizes:** Select "Competition will award prizes" during creation.
- **Add Awards:** In the Overview tab, Tracks and Awards section, create at least one track, and at least one award for each track
- **Documentation:** You must specify prize counts and criteria in the Rules and Overview sections.
- **Fulfillment:** Hosts are solely responsible for distributing prizes and complying with tax rules. Kaggle does not facilitate prize distribution for Community Competitions.

##### (Optional) Evenly Distribute Prizes

Distributing prizes evenly across top submissions, rather than employing a tiered structure, offers several advantages for hackathon hosts. This approach reduces the pressure of meticulously stack-ranking the very best entries against each other and creating a final order of 1st Place - Nth Place. Instead, hosts can focus on confidently identifying a pool of high-quality, winning submissions that meet the hackathon's objectives. This can simplify the final judging process, mitigate potential internal disagreements over marginal differences between top contenders, and ensure that multiple excellent projects are recognized and rewarded equally for their significant contributions.

#### Consider Multiple Tracks

A single competition can offer slightly different problems, emphasis, or participant avenues for evaluation. These tracks should be distinct enough from each other to address different aspects of the problem statement, but still within the same focus of the broader competition. Different tracks can cater to participants with varying expertise, increasing participation.

Examples of different tracks might be: a “Data Visualization Track” with an emphasis on tables and graphics, a “Student Track” limited to student participants, or an “Innovation Track” with an emphasis on novelty over technical proficiency.

Note that multiple tracks might increase complexity in judging if you are adding additional criteria but can also provide an opportunity for external partners to aid in judging a specific portion of the Hackathon (e.g. inviting a Google representative to judge a “Best Gemini App” Track). Hosts should be careful not to try and host too many tracks that may split attention.

![Create a track](https://storage.googleapis.com/kaggle-media/cms/page-images/Docs%20Comps%20Setup%202.gif)*GIF of how to create a track and track awards for your Hackathon*

#### Draft Your Evaluation Rubric

All Kaggle competitions are “contests of skill” (as opposed to a “contest of chance”, like a sweepstake or lottery). As such, participants must have the opportunity to win the competition on the basis of merit, not luck, and understand the criteria being used to evaluate their submissions. In Kaggle Hackathons, this is your “Evaluation Rubric” (or “Judges Rubric”).

Participants should be able to understand how and why a winning submission can achieve a high score, or perform better than others through public, establishing scoring criteria. The host team is responsible for creating a scoring rubric before the competition has launched, and against which all submissions are evaluated.

The best practice for evaluation rubrics is to first outline what components of a submission are necessary to be considered (e.g. a YouTube video is required, an attached notebook must be open-sourced, etc), and beyond that what qualitative elements you’re looking for in a successful, high-quality submission. Describe what each component means to you, and noting how important each component is with a weighted score.

You should publish this rubric in the 'Evaluation' tab (found under the Overview section) of your competition setup so that participants know exactly how they will be judged.

For example, let’s say you’re hosting a competition that challenges users to create a web application that teaches high schoolers how to fine tune large language models, with an accompanied Youtube video for documentation. The following would serve as a good rubrics:

##### Evaluation Rubric Example 1

**Application: Evaluation Rubric (60 points total)**

| Criteria | Points Possible |
| --- | --- |
| Usefulness: The application has a meaningful purpose and functions correctly without errors. | 0-15 points |
| Informativeness: The application includes detailed and accurate documentation. | 0-15 points |
| Engagement: The web application demonstrates an interesting or engaging use case. | 0-10 points |
| Documentation Quality: The web application is well-documented and follows best practices. | 0-15 points |
| Novelty: The web application demonstrates a surprising, new, or novel use case. | 0-5 points |
| Required Elements: The web application is less than 2000 words and uses a minimum of 10 graphics. | Yes/No |

**Video: Evaluation Rubric (40 points total)**

| Criteria | Points Possible |
| --- | --- |
| Accuracy: The video presents accurate information and utilizes current best practices. | 0-10 points |
| Informativeness: The video discusses topics such as prompt engineering and their importance to the project. | 0-10 points |
| Instructional Value: The video serves as a valuable learning resource for Gemini API users. | 0-10 points |
| Entertainment & Production Quality: The video is enjoyable to watch, and the production quality is professional. | 0-10 points |
| Required Elements: The Youtube video is less than 5 minutes | Yes/No |

##### Evaluation Rubric Example 2

**Submission Requirements:**

1. **Video Demo (3 min).** This is the most important part of your submission. Create a dynamic, engaging, and high-quality video that demonstrates your project in action.
   - Goal: Tell a story. Show us the problem and how your Gemma 3n app solves it in a powerful way.
   - Format: You can post your video to YouTube, X (Twitter), TikTok, or any other public platform. You will provide a direct link to the video. It must be viewable by the judges without requiring a login.
2. **Technical Writeup (Kaggle Writeup).** This paper- or blog-style report is your technical verification. It must clearly explain the architecture of your app, how you specifically used Gemma 3n, the challenges you overcame, and why your technical choices were the right ones. Its primary purpose is to prove to the judges that your video demo is backed by real engineering.
3. **Public Code Repository.** Provide a link to a public repository (e.g., GitHub, Kaggle Notebook). The code must be well-documented and clearly show the implementation of Gemma 3n. This is non-negotiable and will be used to validate the authenticity of your project.
4. **Public Project Link.** A URL to your working product or interactive demo. This allows judges to experience your project firsthand, if applicable. It should be publicly accessible and not require a login or paywall.

**Judging Criteria:**

- **Innovation Score (30%)**
  - Would educators be able to use these results on a week-to-week basis?
  - Are the ideas unique?
- **Data Science Score (30%)**
  - Is the work correct?
  - Are claims backed up by data?
  - Are the analytical applications innovative?
- **Documentation Score (20%)**
  - Is the submission well-written?
  - Is the documentation easy to follow?
  - Is the outcome clearly defined?
- **Data Visualization Score (20%)**
  - Are the charts and tables provided accessible?
  - Are the charts and tables accurate?
  - Are the charts and tables innovative?

#### Form a Judges Panel

We recommend a panel of at least 3 judges. But more important to ensuring submissions are graded fairly and effectively is how explicit the criteria is documented. This also makes it easier to onboard people from your team in evaluating valid submissions in early rounds.

##### Adding Judges to your Hackathon

This GIF shows how to designate Kaggle users as judges for your Hackathon. These judges are listed on the competition page, and help winners understand the audience for whom they are writing

![Designate Judges](https://storage.googleapis.com/kaggle-media/cms/page-images/Docs%20Comps%20Setup%204.gif)

#### (Optional) Draft a Writeup Template

A Writeup Template (found in the Settings tab) creates a default template for how Project Writeups should pre-populate for all participants. This can also be an effective way of clearly demonstrating what makes for a better submission than another, and helps get participants started with an outline.

![Writeup Templates](https://storage.googleapis.com/kaggle-media/cms/page-images/Docs%20Comps%20Setup%201.png)*Screenshot of Settings Tab to find where to include Writeup Templates*

#### (Optional) Add a Sample Writeup

A Sample Writeup is an important optional component for a Hackathon because it provides a tangible example of a high-quality submission, offering clarity beyond a simple template.

The creator of the competition can create a Sample Writeup through the Writeups tab. Selecting the + New Writeup tab allows you to draft a Writeup. Once submitted, you may pin it by selecting Set as Sample Project from the dropdown menu on the writeup itself.

#### (Optional) Add a Dataset

You may require the use of data in your hackathon, or provide datasets as inspiration to users. Hackathon participants often collaborate by sharing code publicly throughout the competition, and having a dataset attached to the data page (even if its just a blank readme file!) will allow their notebooks to appear in the Code tab.

#### Finalize & Launch

- **Basic Details:** Upload images and set the "Score Decimals to Display" (truncating decimals can prevent "leaderboard probing").
- **Launch Checklist:** Once all boxes are green, you can launch immediately or schedule it for the future.
- **Inviting:** Share the unique URL found in the Launch Checklist.

#### Judge Submissions

When the competition has concluded, all designated judges of the Kaggle competition will be able to download a CSV with all Writeups and their metadata directly from the Writeups tab. Judges will typically review the submissions (Writeups and attached resources) and record their scores externally according to the rubric. This provides you with the flexibility to evaluate submissions the way you feel is best for your team. There are a number of best practice recommendations Kaggle recommends as well (below), but it's ultimately up to you to decide the winner the way you best see fit according to the evaluation criteria. The host will then use these scores to select and publish winners.

This GIF shows how to export submissions:

![Export Submissions](https://storage.googleapis.com/kaggle-media/cms/page-images/Docs%20Comps%20Setup%206.gif)

The CSV export looks like this: Id Tracks Team\_Name Team\_Members WriteUpUrl Project\_Title Project\_Subtitle Project\_Description Video\_Links Project\_Links

The completed Writeup listing will look something like this:

![Writeup Listing](https://storage.googleapis.com/kaggle-media/cms/page-images/Docs%20Comps%20Setup%203.png)

##### Consider Initial Filtering or Shortlisting

As there can often be a significant volume of submissions to review, we recommend an initial elimination/shortlisting round where 1-2 judges perform a filtering of submissions according to well-defined eligibility criteria to arrive at a final group for detailed review by the broader panel. For example, you may find that a handful of submissions, particularly early ones, are spam or of noticeably low quality (e.g. a large block of code, filled with errors, with no documentation or explanation). These are sometimes due to teams making a placeholder submission early in the competition and never returning to update their work prior to the deadline.

##### Reduce Bias

While there can be a large volume of submissions for your team to review and you may want to look through them quickly, consider that judges’ scoring may need normalization to reduce bias, and a low quality submission by one judge may be a high quality submission by another. Some judges are more lenient, while others are more strict in their evaluation criteria. A few tips to reduce bias:

- Try to ensure each submission is reviewed at least twice, and try not to have judges see the same “sets” of writeups. (We don’t want Writeups 1-20 only compared against writeups 1-20 by the same judges).
- If you held an initial filtering stage, consider having judges randomly select a few "non-finalist" submissions to ensure they were filtered out properly.
- Consider stack ranking and a rank-choice point allocation across judges to avoid point variance and to come to the most complete consensus at the end (e.g. 10 points for 1st, 9 points for 2nd...).

With these two aspects of the evaluation criteria defined (the minimum requirements and the evaluation rubric), this is what the evaluation phase could look like for a typical hackathon:

| Evaluation Resource | Subject | Time |
| --- | --- | --- |
| Initial Pass (Round 1) | Eligibility criteria | 8+ hours |
| Detailed Evaluation (Round 2) | Evaluation rubric | 16+ hours |
| Final deliberation (Round 3) | Jury discussion | 8+ hours |

Note: Time allocations are subject to the number of submissions your Hackathon receives, and the amount of judges on your judging panel.

#### Finalizing Winners

Judges must rigorously vet winning submissions to ensure full compliance with all competition rules and evaluation criteria. It is common for non-winning participants to closely scrutinize the winning entries for any signs of non-compliance. To maintain the integrity of the competition and avoid disputes, it is necessary to ensure fairness through the equal application of rules across all submissions throughout the judging process.

Once you have identified your winners, your final steps are to:

- (optional) Contact them directly via email to notify them that they’ve won, prior to selecting their submissions in the competition. This is not required, but is a nice courtesy so the winners hear they’ve won from the hosts directly instead of passively from the competition page. Kaggle allows you to direct message a limited number of participants each month through the platform.
- Distribute awards to the winning writeups on the Kaggle competition page (see below)
- Make a forum post in the competition highlighting the great submissions, noting the winners have been finalized and that their writeups can be seen on the Writeups Tab. As an added bonus, note any comments made by the judges panel and any progress you're expecting on your problem after the competition closes.
- Consider offering feedback to non-winners upon request. This is also not required, but it’s become customary in Hackathons to allow non-winning participants to solicit feedback on their submissions at a later date (i.e. 6+ weeks after the competition has ended and results are finalized). Kagglers often participate in competitions as a means of learning and improving their skills, and feedback is important to maintaining a healthy, contributing community where participants want to keep coming back and participating in more competitions. While it may not be feasible to release the individual scores of every submission from hundreds of teams, it is well appreciated to provide directional feedback on an as-requested basis to users looking to improve. (e.g. 2-3 bullet points on what a submission did well and what they could improve upon)

![Select Winners](https://storage.googleapis.com/kaggle-media/cms/page-images/Docs%20Comps%20Setup%205.gif)*GIF indicating how to select Hackathon Submissions as Winners*

Contact the winners to coordinate prize distribution and any fulfillment obligations

#### FAQs

##### Can I use AI to judge?

We discourage the use of AI to solely judge Hackathon submissions for a number of reasons.

- Writeups that the LLMs will be grading are comprised of diverse and often unstructured inputs e.g. links to external URLs and web apps
- LLMs are vulnerable to adversarial inputs e.g. jailbreaking
- LLMs give grades that are biased and unfair e.g. self-favoritism
- LLM ratings rarely correlate with human ratings

Early testing shows that AI judges don’t always appropriately select winners, or filter winners into a group for further consideration, when compared with human selections.

If you are going to use an LLM-as-a-judge despite this guidance, you should ensure the following conditions are met:

- Define a problem statement that allows participants to submit well-defined outputs that have a predictable structure.
- Construct an evaluation rubric of binary pass/fail grades rather than using a Likert scale.
- Manually grade a sufficient quantity of suitably realistic submissions.
- Evaluate the accuracy of your LLM-as-a-judge system by comparing your automated grades to your manual grades.
- Thoroughly review best practices e.g. https://hamel.dev/blog/posts/llm-judge/
- ⚠️ If you use AI-powered tools to evaluate submissions, check whether the tool's provider may use submitted content to train its models. Participant submissions may be licensed (e.g., under CC BY 4.0), meaning any downstream use — including as training data — must comply with the license terms, such as providing attribution to the original author. Be transparent with participants about how their work will be processed, and prefer tools with clear data-retention policies.

##### How long should I run my hackathon?

While competition duration is flexible, we recommend a 6 week duration as a starting point. Time span will be determined by problem and evaluation rubric complexity, as well as participant engagement. A rule of thumb to follow is that you want your Hackathon to be live long enough to gain a large participant base, and long enough for participants to create high-quality submissions, but not too long as to lose momentum, or to grow stale as participants wait for results.