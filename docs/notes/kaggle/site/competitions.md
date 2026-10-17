# Competitions

Kaggle Competitions are designed to provide challenges for competitors at all different stages of their machine learning careers. As a result, they are very diverse, with a range of broad types.

***

### Prediction Competitions

These are full-scale supervised machine learning challenges which pose difficult prediction problems. Prediction competitions attract some of the most formidable experts and offer large prize pools. They are a valuable opportunity to learn skills from the very best in the field.

Prediction competitions can take many unique formats, which can impact how you participate.

#### Prediction Competition Formats

##### Classic Competitions

Classic competitions are those which follow the standard Kaggle format. In a simple competition, users can access the complete datasets at the beginning of the competition, after accepting the competition’s rules. As a competitor you will download the data, build models on it locally or in Kaggle Notebooks, generate a prediction file, then upload your predictions as a submission on Kaggle.

Examples include:

- [American Express Default Prediction](https://www.kaggle.com/competitions/amex-default-prediction) – Use customers’ shopping history to predict if they will default in the future.
- [Jigsaw Toxic Comment Classification Challenge](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge) – Predict the existence and type of toxic comments on Wikipedia.
- [Google Landmark Retrieval Challenge](https://www.kaggle.com/c/landmark-retrieval-challenge) – Given an image, find all the same landmarks in a dataset.
- [Right Whale Recognition](https://www.kaggle.com/c/noaa-right-whale-recognition) – Identify endangered right whales in aerial photographs.

##### Code Competitions

In these competitions, all submissions must be made from inside a Kaggle Notebook. You cannot upload predictions directly.

- **Balance:** Every user has the same hardware allowances.
- **Simplicity:** Models must run within platform compute constraints.
- **Constraints:** Notebooks may be restricted by CPU/GPU runtime, internet access, or external data usage.

###### Code Competition FAQ

- **Errors:** See the [debugging page](https://www.kaggle.com/code-competition-debugging).
- **External Data:** Only allowed if specified by the competition rules.
- **Compute Limits:** Limits (RAM, CPU, etc.) are visible within the editor.
- **Winners:** Often determined by rerunning the Notebook on a private test set after the deadline.

Examples Include:

- [The Konwinski Prize](https://www.kaggle.com/competitions/konwinski-prize) – $1M for the AI that can close 90% of new GitHub issues.
- [Detect AI Generated Text](https://www.kaggle.com/competitions/llm-detect-ai-generated-text) - Identify which essay was written by a large language model.

##### Two-stage Competitions

Some Code Competitions are split into Stage 1 and Stage 2. Stage 2 involves a new test dataset previously unavailable until the start of that stage. Your code will be run on the new test dataset, and your final score will be based on your submissions performance on that unseen set. A common pitfall of participants in two-stage competitions is not writing their notebook in a way that is flexible enough to adapt to a new, unseen test set!

Examples Include:

- [Zillow Prize](https://www.kaggle.com/c/zillow-prize-1) – Build a machine learning algorithm that can challenge Zestimates.
- [Jane Street Real-Time Market Data Forecasting](https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting) - Predict financial market responders using real-world data.

#### Getting Started and Playground Competitions

Getting Started competitions are the most approachable competitions, centered around a specific machine learning technique or data format and are meant for new users to get their foot in the door. They offer no prizes or points and are heavily tutorialized.

- [Digit Recognizer](https://www.kaggle.com/c/digit-recognizer)
- [Titanic: Machine Learning from Disaster](https://www.kaggle.com/c/titanic) – Predict survival on the Titanic.
- [Housing Prices: Advanced Regression Techniques](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)

*Note: Getting Started Competitions have two-month rolling leaderboards. Submissions older than two months are invalidated to allow new Kagglers to compare scores against a current cohort rather than tens of thousands of historical users.*

Playground competitions are “for fun” type of competition one step above "Getting Started." These provide relatively simple tasks in a lower-stakes setting. Prizes are typical kudos and public recognition.

- [Dogs versus Cats](https://www.kaggle.com/c/dogs-vs-cats)
- [Leaf Classification](https://www.kaggle.com/c/leaf-classification)
- [New York City Taxi Trip Duration](https://www.kaggle.com/c/nyc-taxi-trip-duration)

#### Making a Submission

Submission limits (usually 5 per day) apply to the whole team.

##### Submitting by Uploading

In Classic Competitions, use the "Submit Predictions" button to upload your .csv file. It must pass processing to receive a score.

##### Submitting from a Notebook

In Code Competitions:

1. Initialize a Notebook with the competition dataset.
2. Generate a submission file (e.g., submission.csv) in /kaggle/working.
3. Click "Save Version" -&gt; "Save & Run All".
4. From the Notebook Viewer, go to the Output section and click Submit.

*Note: Some code competitions require you to submit your code in a specific template. This will be provided as a demo notebook in the competition.*

#### The Leaderboard

- **Public Leaderboard:** Visible during the competition; based on a sample of test data.
- **Private Leaderboard:** The final ranking based on the remainder of the test data.
- **Overfitting:** A high public score doesn't guarantee a high private score. Avoid "chasing" the public leaderboard.

#### Leakage

Data Leakage is the presence of unexpected information in training data that allows for unrealistically high performance but fails in the real world.

Examples of Leakage:

- Leaking ground truth into the test set.
- Information from the future leaking into the past.
- Hidden "proxy" variables (e.g., a "surgery" variable predicting a "cancer" diagnosis).

Kaggle may address leakage by relaunching a competition or generating a new test set.

***

### Hackathon Competitions

Kaggle Hackathons are a form of competition where you may be asked to perform any variety of unique data tasks such as building an app, developing a new metric, creatively using an LLM, or producing an educational YouTube video. These competitions move beyond traditional predictive modeling, opening up new problem-solving avenues for development and innovation.

While supervised machine learning competitions (i.e. “Prediction competitions”) require a dataset, ground truth (answer key) that is both known and private, and an evaluation metric, a Hackathon allows users to build creative, diverse solutions to more open-ended, subjective challenges. If a Prediction competition is similar to a math test, then a Hackathon is similar to a term paper.

Here are a few areas of nuanced consideration that your team should consider when developing your hackathon.

Examples Include:

- [Gemma 3n Impact Challenge](https://www.kaggle.com/competitions/google-gemma-3n-hackathon/overview) - build your best products for a better world using the latest Gemma model.
- [OpenAI to Z Challenge](https://www.kaggle.com/c/openai-to-z-challenge) - Use OpenAI o3/o4 mini and GPT 4.1 models to help identify possibly hidden archeological sites.
- [Vibe Code with Gemini 3 Pro in AI Studio](https://www.kaggle.com/competitions/gemini-3/overview) - Build with Gemini 3 and compete for $500,000 in credits.
- [NFL Big Data Bowl](https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics) - Understand player movement while the ball is in the air.

#### Making a Submission

A valid submission is made via Kaggle Writeup, which gives a dedicated space to tell the story behind your data science project. While the Writeup is your final report, you will often use Kaggle Notebooks to perform your analysis and generate visualizations, which you can then link to or embed within your Writeup. Writeups allow for you to add multimedia galleries (great for walkthrough videos), link to external resources like GitHub or Hugging Face with rich embedded cards, annotate those links to provide context and explain why they matter.

Each Hackathon may also require you to attach notebooks, links, or additional content for consideration by the judges. See the specific evaluation criteria for more detail.

##### How to Create a Writeup

The Kaggle Writeup serves as your project report. This should include a title, subtitle, and a detailed analysis of your submission. You must select a Track for your Writeup in order to submit. Tracks are specific categories or problem areas defined by the host (e.g., 'Visualization Track' vs. 'Innovation Track') that may have different evaluation criteria or prizes. Make sure to check the competition evaluation page to see if you can submit to multiple tracks or if you must choose just one

To create a new Writeup, click on the "New Writeup" button from a competition page. After you have saved your Writeup, you should see a "Submit" button in the top right corner.

Your final Submission must be made prior to the deadline. Any un-submitted or draft Writeups by the competition deadline will not be considered by the Judges.

*Note: If you attach a private Kaggle Resource to your public Kaggle Writeup, your private Resource will automatically be made public after the deadline.*

All of the content on Kaggle is written in [Markdown](https://github.com/showdownjs/showdown/wiki/Showdown's-Markdown-syntax). If you are copy-pasting from another application, like Word or your browser, you may need to clean up the markdown or html for things to display properly.

##### Submission Requirements

Each competition will outline the required elements that need to be included in your writeup to be considered by judges. This may include notebooks, datasets, videos, papers, links to working apps, or more. Should your submission not include one of these requirements, it may be subject to disqualification or penalty by the judges.

Be sure that any external links do not require logins or contain paywalls, so that they can be accessible to the judges for review.

##### Evaluation Criteria

All Kaggle competitions are “contests of skill” (as opposed to a “contest of chance”, like a sweepstake or lottery). Winners of Hackathons are evaluated by a panel of judges, using a pre-established scoring criteria. The host team is responsible for creating a scoring rubric before the competition has launched, and against which all submissions are evaluated.

The evaluation section describes how submissions will be scored and how participants should format their submissions. An example may be:

**Application: Evaluation Rubric (60 points total)**

| Criteria | Points Possible |
| --- | --- |
| Usefulness: The application has a meaningful purpose and functions correctly without errors. | 0-15 points |
| Informativeness: The application includes detailed and accurate documentation. | 0-15 points |
| Engagement: The web application demonstrates an interesting or engaging use case. | 0-10 points |
| Documentation Quality: The web application is well-documented and follows best practices. | 0-15 points |
| Novelty: The web application demonstrates a surprising, new, or novel use case. | 0-5 points |

**Video: Evaluation Rubric (40 points total)**

| Criteria | Points Possible |
| --- | --- |
| Accuracy: The video presents accurate information and utilizes current best practices. | 0-10 points |
| Informativeness: The video discusses topics such as prompt engineering and their importance to the project. | 0-10 points |
| Instructional Value: The video serves as a valuable learning resource for Gemini API users. | 0-10 points |
| Entertainment & Production Quality: The video is enjoyable to watch, and the production quality is professional. | 0-10 points |

##### Tracks and Awards

A single competition can offer slightly different problems, emphasis, or participant avenues for evaluation. These tracks address different aspects of the problem statement, but still within the same focus of the broader competition. Different tracks may also cater to participants with varying expertise or backgrounds.

Examples of different tracks might be: a “Data Visualization Track” with an emphasis on tables and graphics, a “Student Track” limited to student participants, or an “External Tooling Track” with an emphasis on using partner tools.

##### Winner Selection

Submissions are made private until the end of a Hackathon, at which point all submissions are made public for review by the Judges and Kaggle community. The judging team will review submissions and select winners, which will be displayed on the competition’s Winners tab.

Note, it may take a number of weeks for judges to complete review of submissions, especially when competition participation is high. Judges are also rarely able to provide individualized feedback or scores to all participants.

***

### Simulation Competitions

Instead of making predictions against a static dataset, simulations host dynamic environments. Your submission is an agent which compete against other participants' agents in a game or simulated environment. The environment rules outline the terms of the competition, and submissions are matched against similar skilled opponents, playing multiple episodes to establish the leaderboard.

Examples Include:

- [Halite](https://www.kaggle.com/competitions/halite/overview) by Two Sigma
- [Lux AI](https://www.kaggle.com/c/lux-ai-2021) by the Lux AI Challenge

#### Simulation Evaluation

Each Submission has an estimated Skill Rating which is modeled by a Gaussian $N(\mu,\sigma^2)$ where $\mu$ is the estimated skill and $\sigma$ represents our uncertainty of that estimate which will decrease over time.

When you upload a Submission, we first play a Validation Episode where that Submission plays against copies of itself to make sure it works properly. If the Episode fails, the Submission is marked as Error. Otherwise, we initialize the Submission with $\mu\_0=600$ and it joins the pool of All Submissions for ongoing evaluation. We repeatedly run Episodes from the pool of All Submissions, and try to pick Submissions with similar ratings for fair matches.

After an Episode finishes, we'll update the Rating estimate for all Submissions in that Episode. If one Submission won, we'll increase its $\mu$ and decrease its opponent's $\mu$ -- if the result was a draw, then we'll move the two $\mu$ values closer towards their mean. The updates will have magnitude relative to the deviation from the expected result based on the previous $\mu$ values, and also relative to each Submission's uncertainty $\sigma$. We also reduce the $\sigma$ terms relative to the amount of information gained by the result. The score by which your agent wins or loses an Episode does not affect the skill rating updates.

Every agent submitted will continue to play episodes beyond the submission deadline. On the leaderboard only your best scoring agent will be shown.

The goal of this process is to accurately rank competition participants by repeatedly pairing their automated submissions against opponents of similar skill levels using a dynamic rating system. By simulating numerous matches and refining statistical estimates of performance, the system ensures the final leaderboard reflects the true skill of each user's best-performing agent.

***

### Resources for Getting Started

- **Learning:** [Kaggle Learn](https://www.kaggle.com/learn/overview) for hands-on tracks.
- **Videos:** [What Kaggle has learned](https://www.youtube.com/watch?v=oYNKc_u9Os8) and [How to (almost) win at Kaggle](https://www.youtube.com/watch?v=JyEm3m7AzkE).
- **Forums:** [General Discussion](https://www.kaggle.com/discussion), [Questions & Answers](https://www.kaggle.com/questions-and-answers), and [Kaggle Noobs Slack](https://kagglenoobs.slack.com/).
- **Blog:** [No Free Hunch](http://blog.kaggle.com/) for winner interviews and technical tutorials.

### Joining a Competition

Check the [Competitions listing](https://www.kaggle.com/competitions) for active challenges.

- **Rules Tab:** You must accept the rules before downloading data or submitting.
- **Overview Tabs:** Review the Description, Data, Evaluation, Timeline, and Prizes.
- **Timeline:** Watch for the Rules Acceptance Deadline and the Submission Deadline.

### Forming a Team

Everyone competes as a team (even if it's a team of one).

- **Merging:** You can invite others to merge teams until the Team Merger Deadline.
- **Limits:** Merging is not allowed if the combined team exceeds the size limit or the historical submission limit.
- **Team Leader:** The primary point of contact with modification privileges.

### Cheating

Cheating is taken very seriously. Kaggle monitors for plagiarism and voting rings. Violations can result in removal from leaderboards or permanent account bans. Report suspicious activity to the [compliance account](https://www.kaggle.com/compliance).