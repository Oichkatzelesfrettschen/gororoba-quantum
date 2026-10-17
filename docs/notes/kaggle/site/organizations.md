# Organizations

***

### Overview

Anyone can create an organization profile on Kaggle. Organization profiles allow anyone in the community to find your organization's datasets, models, and competitions in one place.

Before creating an organization, it's helpful to understand how organization profiles work.

***

### How do organization profiles work

#### What are organizations for?

Organization profiles are a "landing page" for your organization's published competitions, models, and datasets. For example, it gives you an easy way to share (and other users to find) all of the datasets and models that your team has published with a single link.

#### What are organizations NOT for?

Organizations are not meant to be used as a tool for collaboration with a group of people. You should use [Kaggle groups](/groups) for this purpose.

Note: While all members of an organization can create competitions, datasets, and models as an organization, this does not give other members of the organization the ability to manage that content (edit, delete, update, or view private resources). Read more about organization permissions below.

#### Who should create and use organization profiles?

For research labs, whether part of a university or industry corporation, organization profiles provide a way to organize the models and datasets your team has published in one place. For large companies, an organization profile will display all of the competitions you've hosted.

For professors, we recommend using a [Kaggle group](/groups) to make it easier to see and manage datasets, notebooks and models you share in your classes.

***

### Creating a new organization profile

#### Creation

Anyone with a Kaggle account can request the creation of an organization profile. To start the process, sign in to your Kaggle account, and then fill out the [new Organization request form](https://www.kaggle.com/contact#/organizations/request-creation).

You'll need to provide the following information:

- **Name**: The name of your organization
- **URL**: You should edit this to something that's short. All links to this organization page will start with this URL, e.g., any datasets or models it owns.
- **Moderation Details**: Some information you share won't appear on your organization profile page, but will be used by our team to review your organization for approval. For example, proof your organization exists outside of Kaggle, your organization's purpose, and your role in the organization.

You'll be able to set the following on your organization profile page after it has been created:

- **Overview**: A "bio" or long description for your organization
- **Tagline**: A short description of your organization
- **Website**: A URL to your organization website
- **Image**: A 400 x 400px image of your organization logo

You'll also be able to change or update most details of your organization freely on the organization profile page, as well as invite members to your organization, and more.

Once you complete the new organization request form, your organization will be reviewed by the Kaggle team for approval, before it's created. Continue to the next section "Review" to learn more about the next steps.

#### Review

Please be patient while your organization is being reviewed by the Kaggle team.

If you have questions about the review process or you would like to appeal a review, please see our contact page: https://www.kaggle.com/contact#/other/issue

#### Approval

Once your organization has been approved, you'll receive an email and/or site notification. You and other members of the organization can now create organization-owned datasets, models, or competitions including making them public. Anyone can also see your organization's profile page.

***

### Organization member permissions

#### Abilities of organization members

Organization members can create datasets, models, and competitions under approved organization profiles.

Again, organizations are not currently meant to be used as a tool for collaboration with a group of people. While all members of an organization can create competitions, datasets, and models as an organization, this does not give other members of the organization the ability to manage that content (edit, delete, update, or view private resources).

If you want to share private datasets or models owned by an organization profile, you will need to use Collaboration features.

Similarly, organization members are NOT able to see any unlaunched competitions unless their user is the creator of the competition.

Members will not be able to add new members to an organization unless the organization owner shares the unique invitation link.

#### Abilities of organization admins

Organization admins have the same abilities and permissions as organization members. In addition, they can add and remove members, transfer ownership of the organization to another member, and edit information about the organization (logo, tagline, description, etc.).

***

### How to create content as an organization

#### Competitions

Anyone can host a community competition, by clicking the "+Create" button in the upper lefthand corner of any page on Kaggle and selecting "Competition." In order to associate your competition with an organization profile that you are an admin or member of, simply choose your organization from the "Creating As" dropdown.

When a competition is created under an organization profile, the competition will feature your organization's logo and the competition will show up on the "Competitions" tab of your organization's profile page.

When a competition is created under an organization profile, there are NO changes to who can see or manage your competition. That is, other members of the organization cannot see an unlaunched competition and they cannot manage the settings of your competition when it is launched.

#### Datasets and Models

Anyone can publish datasets or models, by clicking the "+Create" button in the upper lefthand corner of any page on Kaggle and selecting "Dataset" or "Model". In order to associate your dataset or model with an organization profile that you are an admin or member of, simply choose your organization from the "Creating As" dropdown.

When a competition is created under an organization profile, the dataset or model will feature your organization's logo and the dataset or model will show up on the "Datasets" or "Models" tab respectively of your organization's profile page.

When a dataset or model is created under an organization profile, other members will be able to see it while it's private. There are NO changes to who can see or manage your datasets or models created under an organization profile. That is, other members of the organization cannot cannot edit, delete, or update the datasets or models unless they are separately added as edit collaborators on the "Settings" tab of the dataset or model.

#### Transferring Resources to an Organization

You can transfer ownership of resources you own to any Organization of which you are a member. Only the owner of the resource can transfer ownership. To transfer ownership, navigate to the resource's detail page and select the "Settings" tab. Scroll down to the "Sharing" section and click "Transfer Ownership", select the Organization you're transferring the resource to and click "Done". Transferring ownership to an organization is not reversible.

***

### Model Gating for Organizations

#### What are Gated Models

A gated model is a model on Kaggle that requires users to agree to a specific agreement and potentially provide information before they can access it. This agreement can include terms of use, privacy policy links, and a form for collecting user data.

#### Using Model Gating

To use model gating, start by contacting Kaggle to get permission for your organization and then log in with editor permissions for your model. Enable model gating on the "Settings" tab and customize the gating agreement, specifying review mode (automatic or manual), privacy policy URL, and agreement content in YAML format, which includes title, description, and fields for collecting user information. More details about how to use YAML to create an agreement can be found in [this page](/model-gating-json-schema).

After enabling gating, manage user consents via UI or API. The API allows listing and reviewing consents, filtering by review status and data expiration. Consents can be approved or rejected, and user data can be downloaded before it expires, adhering to your privacy policy. Users accessing the gated model will be prompted to agree and provide information, with their access status displayed.

#### Gating Publisher API

The base URL for the HTTP endpoints below is [https://www.kaggle.com](https://www.kaggle.com). The Authorization header uses [HTTP Basic auth](https://en.wikipedia.org/wiki/Basic_access_authentication): `Authorization: Basic <base64-encoded-token>`. The *base64-encoded-token* token can be created using the username & key generated from [your Kaggle user settings page](/settings). The username used for authorization also has to be a member of your organization on Kaggle.

| Method | URL | Description | Parameters |
| --- | --- | --- | --- |
| GET | /api/v1/models/{owner\_slug}/{model\_slug}/user-consents | This endpoint retrieves a list of user consents for a specific gated model under the current agreement, with filtering options by review status and expiration of user request data. | <ul><li><em>owner_slug</em> (in path, required): The model owner slug.</li><li><em>model_slug</em> (in path, required): The model slug, e.g., my_gated_model.</li><li><em>review_status</em>=&lt;null\|pending\|accepted\|rejected&gt;: Filter by review status. Default all (null).</li><li><em>is_user_request_data_expired</em>=&lt;null\|true\|false&gt;: Filter by user request data expiration status. Default all (null).</li><li><em>next_page_token</em>: Token for retrieving the next page in paginated results.</li></ul> |
| POST | /api/v1/models/{owner\_slug}/{model\_slug}/user-consents/review | This endpoint reviews user consent. It requires user\_name and review\_status. Publishers can add notes. | <ul><li><em>owner_slug</em> (in path, required): The model owner slug, this is usually your organization name.</li><li><em>model_slug</em> (in path, required): The model slug, e.g., my_gated_model.</li><li><em>user_name</em> (required): The user to whom the review decision is made. These are usually returned in the response of the List API above.</li><li><em>review_status</em> (required)=&lt;pending\|accepted\|rejected&gt;: The decision on the status of the review.</li><li><em>publisher_notes</em>: optional notes.</li></ul> |