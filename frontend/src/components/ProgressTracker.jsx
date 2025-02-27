import React from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  LinearProgress,
  Typography,
  Paper,
} from '@mui/material';

const steps = [
  {
    label: 'App Analysis',
    description: 'Analyzing app metrics and performance',
  },
  {
    label: 'Competitor Analysis',
    description: 'Comparing with competitor apps',
  },
  {
    label: 'Keyword Analysis',
    description: 'Analyzing keyword performance and trends',
  },
];

const ProgressTracker = ({ current, total, error }) => {
  const activeStep = Math.max(0, current - 1);
  const progress = total > 0 ? (current / total) * 100 : 0;

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ width: '100%' }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((step, index) => {
            const stepProps = {};
            const labelProps = {};

            if (error && index === activeStep) {
              labelProps.error = true;
            }

            return (
              <Step key={step.label} {...stepProps}>
                <StepLabel {...labelProps}>
                  {step.label}
                  <Typography
                    variant="caption"
                    display="block"
                    color="text.secondary"
                    sx={{ mt: 0.5 }}
                  >
                    {step.description}
                  </Typography>
                </StepLabel>
              </Step>
            );
          })}
        </Stepper>

        <Box sx={{ mt: 3 }}>
          <LinearProgress
            variant="determinate"
            value={progress}
            color={error ? 'error' : 'primary'}
          />
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              mt: 1,
            }}
          >
            <Typography variant="body2" color="text.secondary">
              {current} of {total} steps completed
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {Math.round(progress)}%
            </Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default ProgressTracker;