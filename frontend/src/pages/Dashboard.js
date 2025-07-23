// TODO: Connect to backend API for metrics, charts, and recent activity
import React from 'react';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

const metrics = [
  { label: 'Total Emails', value: 0 },
  { label: 'Total Transactions', value: 0 },
  { label: 'Financial Emails', value: 0 },
  { label: 'Extraction Success Rate', value: '0%' },
];

const pieData = [
  { name: 'Intent A', value: 0 },
  { name: 'Intent B', value: 0 },
];
const COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'];

const barData = [
  { name: 'USD', count: 0 },
  { name: 'INR', count: 0 },
];

const recentEmails = [];

const Dashboard = () => {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, color: '#1f77b4', textAlign: 'center' }}>
        🤖 Finance Agent Dashboard
      </Typography>
      {/* Metrics Section */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {metrics.map((metric, idx) => (
          <Grid item xs={12} sm={6} md={3} key={metric.label}>
            <Card sx={{ borderLeft: '4px solid #1f77b4', background: '#f0f2f6' }}>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">
                  {metric.label}
                </Typography>
                <Typography variant="h5" sx={{ mt: 1 }}>
                  {metric.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      {/* Charts Section */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>
                📈 Email Classification Distribution
              </Typography>
              <PieChart width={320} height={220}>
                <Pie
                  data={pieData}
                  cx={150}
                  cy={100}
                  innerRadius={40}
                  outerRadius={70}
                  fill="#8884d8"
                  paddingAngle={5}
                  dataKey="value"
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>
                💰 Currency Distribution
              </Typography>
              <BarChart width={320} height={220} data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#1f77b4" />
              </BarChart>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Recent Activity Section */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            🕒 Recent Activity
          </Typography>
          {recentEmails.length === 0 ? (
            <Typography color="textSecondary">No recent emails found</Typography>
          ) : (
            recentEmails.map((email, idx) => (
              <Box key={idx} sx={{ mb: 2 }}>
                <Typography variant="subtitle2">{email.subject}</Typography>
                <Typography variant="body2">From: {email.sender}</Typography>
                <Typography variant="body2">Date: {email.date}</Typography>
                <Typography variant="body2">{email.body}</Typography>
              </Box>
            ))
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard; 