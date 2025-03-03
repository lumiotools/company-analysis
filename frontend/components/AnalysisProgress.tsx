/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

const AnalysisProgress = ({ fundName = "8 Bit Capital" }) => {
  const [seconds, setSeconds] = React.useState(0);
  const [minutes, setMinutes] = React.useState(0);
  const [progress, setProgress] = React.useState(0);
  const [currentStage, setCurrentStage] = React.useState(0);
  const [ellipsis, setEllipsis] = React.useState("");
  const [initialTimerComplete, setInitialTimerComplete] = React.useState(false);

  const initialStages = [
    "Extracting raw data",
    "Processing data",
    "Creating company excel",
    "Creating company document",
    "Compiling your data",
  ];

  const extraStages = ["Compiling Analysis", "Preparing Final Results"];

  // Total duration in seconds (2.5 minutes)
  const totalDuration = 250;
  // Extra stage duration in seconds (30 seconds each)
  const extraStageDuration = 30;

  // Automatically increment timer and progress
  React.useEffect(() => {
    let timer;

    if (!initialTimerComplete) {
      // Initial 2.5-minute timer
      timer = setInterval(() => {
        setSeconds((prevSeconds) => {
          if (prevSeconds === 59) {
            setMinutes((prevMinutes) => prevMinutes + 1);
            return 0;
          }
          return prevSeconds + 1;
        });

        // Update progress percentage
        setProgress((prev) => {
          const newProgress =
            ((minutes * 60 + seconds + 1) / totalDuration) * 100;
          return Math.min(newProgress, 100);
        });

        // Update current stage based on progress
        const newStageIndex = Math.floor(
          (progress / 100) * initialStages.length
        );
        if (
          newStageIndex !== currentStage &&
          newStageIndex < initialStages.length
        ) {
          setCurrentStage(newStageIndex);
        }

        // Check if initial timer is complete
        if (minutes * 60 + seconds + 1 >= totalDuration) {
          setInitialTimerComplete(true);
          // Start with the first extra stage
          setCurrentStage(initialStages.length);
        }
      }, 1000);
    } else {
      // Extra stages timer (30 seconds each, looping)
      timer = setInterval(() => {
        // Increment seconds for visual purposes
        setSeconds((prevSeconds) => {
          if (prevSeconds === 59) {
            setMinutes((prevMinutes) => prevMinutes + 1);
            return 0;
          }
          return prevSeconds + 1;
        });

        // Toggle between the two extra stages every 30 seconds
        const totalSeconds = minutes * 60 + seconds - totalDuration;
        if (totalSeconds % extraStageDuration === 0 && totalSeconds > 0) {
          setCurrentStage((prevStage) => {
            // Toggle between the two extra stages
            return prevStage === initialStages.length
              ? initialStages.length + 1
              : initialStages.length;
          });
        }
      }, 1000);
    }

    // Handle ellipsis animation
    const ellipsisTimer = setInterval(() => {
      setEllipsis((prev) => {
        if (prev === "...") return "";
        return prev + ".";
      });
    }, 500);

    return () => {
      clearInterval(timer);
      clearInterval(ellipsisTimer);
    };
  }, [minutes, seconds, progress, currentStage, initialTimerComplete]);

  // Get the current display stage
  const getCurrentStage = () => {
    if (!initialTimerComplete) {
      return initialStages[currentStage];
    } else if (currentStage === initialStages.length) {
      return extraStages[0];
    } else {
      return extraStages[1];
    }
  };

  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto p-4 font-sans">
      <h1 className="text-2xl font-bold mb-4">
        Started analysis for {fundName} {ellipsis}
      </h1>

      <div className="relative w-full h-4 bg-blue-100 rounded-md overflow-hidden mb-2">
        <div
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-1000 ease-linear"
          style={{ width: `${initialTimerComplete ? 99 : progress}%` }}
        />
        <div className="absolute top-0 right-0 h-full flex items-center pr-2 text-white font-medium text-sm">
          {initialTimerComplete ? 99 : progress.toFixed(0)}%
        </div>
      </div>

      <div className="flex justify-between items-center">
      <div className="text-xl font-medium text-gray-700">
        {`${minutes}m ${seconds}s`}
      </div>

      <p className="text-sm">Estimated time: 1-5m</p>
      </div>

      <div className="mt-6">
        <div className="transition-all duration-500">
          {getCurrentStage()}
          <span className="ml-1">{ellipsis}</span>
        </div>
      </div>
    </div>
  );
};

export default AnalysisProgress;
