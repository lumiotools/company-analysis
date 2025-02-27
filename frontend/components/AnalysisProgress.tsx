/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useState, useEffect } from "react";

const AnalysisProgress = ({ fundName = "8 Bit Capital" }) => {
  const [seconds, setSeconds] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState(0);
  const [ellipsis, setEllipsis] = useState("");

  const stages = [
    "Extracting raw data",
    "Processing data",
    "Creating company excel",
    "Creating company document",
    "Compiling your data",
    "Done! Please find your data below",
  ];

  // Total duration in seconds (5 minutes)
  const totalDuration = 300;

  // Automatically increment timer and progress
  useEffect(() => {
    const timer = setInterval(() => {
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
      const newStageIndex = Math.floor((progress / 100) * (stages.length - 1));
      if (newStageIndex !== currentStage && newStageIndex < stages.length) {
        setCurrentStage(newStageIndex);
      }
    }, 1000);

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
  }, [minutes, seconds, progress, currentStage, stages.length]);

  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto p-4 font-sans">
      <h1 className="text-2xl font-bold mb-4">
        Started analysis for {fundName}{" "}
        {currentStage < stages.length - 1 ? ellipsis : ""}
      </h1>

      <div className="relative w-full h-4 bg-blue-100 rounded-md overflow-hidden mb-2">
        <div
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-1000 ease-linear"
          style={{ width: `${progress}%` }}
        />
        <div className="absolute top-0 right-0 h-full flex items-center pr-2 text-white font-medium text-sm">
          {progress.toFixed(0)}%
        </div>
      </div>

      <div className="text-xl font-medium text-gray-700">
        {minutes}m {seconds}s
      </div>

      <div className="mt-6">
        <div className="transition-all duration-500">
          {currentStage < stages.length - 1 ? (
            <>
              {stages[currentStage]}
              <span className="ml-1">{ellipsis}</span>
            </>
          ) : (
            stages[currentStage]
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalysisProgress;
