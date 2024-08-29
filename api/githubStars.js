import fetch from 'node-fetch';

export default async function handler(req, res) {
    const { username, device } = req.query;
    const token = process.env.GITHUB_TOKEN;

    if (!username || !token) {
        return res.status(400).json({ error: 'Username and GitHub token are required' });
    }
	
    try {

        const totalStars = await getTotalStars(username, token);
        res.status(200).json({ totalStars });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
}

async function getTotalStars(username, token) {
    let totalStars = 0;
    let page = 1;
    const perPage = 100;

    while (true) {
        const url = `https://api.github.com/users/${username}/repos?per_page=${perPage}&page=${page}`;
        const headers = {
            'Authorization': `token ${token}`
        };

        const response = await fetch(url, { headers });
        if (!response.ok) {
            throw new Error(`Error fetching repositories: ${response.status}`);
        }

        const repos = await response.json();
        if (repos.length === 0) {
            break;
        }

        totalStars += repos.reduce((sum, repo) => sum + repo.stargazers_count, 0);
        page += 1;
    }

    return totalStars;
}