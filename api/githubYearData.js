import fetch from 'node-fetch';

const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

export default async function handler(req, res) {
    const { username, license, device } = req.query;

    try {

        const totalContributions = await fetchTotalContributions(username);

        res.status(200).json(totalContributions);
    } catch (error) {
        console.error('Error fetching or rendering totalContributions:', error);
        res.status(500).json({ error: 'Failed to fetch or render totalContributions' });
    }
}

async function fetchTotalContributions(username) {
    const query = `
    {
        user(login: "${username}") {
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }
    `;

    const TOKEN = process.env.GITHUB_TOKEN;

    if (!TOKEN) {
        throw new Error('GitHub token is not set in the environment variables');
    }

    try {
        const response = await fetch('https://api.github.com/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TOKEN}`,
                'User-Agent': USER_AGENT
            },
            body: JSON.stringify({ query })
        });

        console.log('GitHub API Response:', response.status);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(`GitHub API error: ${result.message}`);
        }

        if (!result.data || !result.data.user || !result.data.user.contributionsCollection) {
            throw new Error(`GitHub API returned unexpected response: ${JSON.stringify(result)}`);
        }

        return result.data.user.contributionsCollection.contributionCalendar;
    } catch (error) {
        console.error('Error fetching totalContributions:', error.message);
        throw new Error(`Error fetching totalContributions: ${error.message}`);
    }
}