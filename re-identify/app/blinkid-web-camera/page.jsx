"use client";

import * as BlinkIDSDK from "@microblink/blinkid-in-browser-sdk";
import Head from "next/head";
import { useEffect, useRef, useState } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import OcrIdVerificationResult from "../components/OcrIdVerificationResult";

export default function BlinkIDWebcamPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processingResult, setProcessingResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanFeedback, setScanFeedback] = useState(
    "Pointez la caméra sur le recto du document."
  );
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const sdkRef = useRef(null);
  const videoRecognizerRef = useRef(null);
  const scanFeedbackLockRef = useRef(false);
  const [isMounted, setIsMounted] = useState(false);

  // Mark component as mounted on client
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Initialisation du SDK
  useEffect(() => {
    const initializeBlinkID = async () => {
      if (!BlinkIDSDK.isBrowserSupported()) {
        setError("Ce navigateur n'est pas supporté !");
        return;
      }

      setIsLoading(true);
      const licenseKey = process.env.NEXT_PUBLIC_BLINKID_LICENSE_KEY;
      const loadSettings = new BlinkIDSDK.WasmSDKLoadSettings(licenseKey);

      loadSettings.allowHelloMessage = true;
      loadSettings.engineLocation = "/resources";
      loadSettings.workerLocation = "/resources/BlinkIDWasmSDK.worker.min.js";

      try {
        const sdk = await BlinkIDSDK.loadWasmModule(loadSettings);
        sdkRef.current = sdk;
      } catch (err) {
        setError("Échec du chargement du SDK !");
        toast.error("Échec du chargement du SDK !");
        console.error("Échec du chargement du SDK !", err);
      } finally {
        setIsLoading(false);
      }
    };

    initializeBlinkID();
  }, []);

  // Démarrer le scan lorsque isScanning change
  useEffect(() => {
    if (
      !isScanning ||
      !sdkRef.current ||
      !videoRef.current ||
      !canvasRef.current
    )
      return;

    const startScan = async () => {
      setError(null);
      setProcessingResult(null);
      setScanFeedback("Pointez la caméra sur le recto du document.");

      const multiSideRecognizer =
        await BlinkIDSDK.createBlinkIdMultiSideRecognizer(sdkRef.current);
      const drawContext = canvasRef?.current?.getContext("2d");

      if (!drawContext) {
        setError("Échec de l'obtention du contexte du canvas");
        toast.error("Échec de l'obtention du contexte du canvas");
        setIsScanning(false);
        setIsLoading(false);
        return;
      }

      const callbacks = {
        onQuadDetection: (quad) => drawQuad(quad, drawContext),
        onDetectionFailed: () =>
          updateScanFeedback("Échec de la détection", true),
        onFirstSideResult: () => {
          updateScanFeedback("Retournez le document pour scanner le verso.");
          toast.info("Retournez le document pour scanner le verso.", {
            position: "top-center",
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
          });
        },
      };

      const recognizerRunner = await BlinkIDSDK.createRecognizerRunner(
        sdkRef.current,
        [multiSideRecognizer],
        false,
        callbacks
      );

      try {
        const videoRecognizer =
          await BlinkIDSDK.VideoRecognizer.createVideoRecognizerFromCameraStream(
            videoRef.current,
            recognizerRunner
          );
        videoRecognizerRef.current = videoRecognizer;

        videoRecognizer.startRecognition(async (recognitionState) => {
          if (!videoRecognizer) return;

          videoRecognizer.pauseRecognition();

          if (recognitionState === BlinkIDSDK.RecognizerResultState.Empty)
            return;

          const result = await multiSideRecognizer.getResult();
          if (result.state === BlinkIDSDK.RecognizerResultState.Empty) return;

          const parsedResult = parseResults(result);
          setProcessingResult(parsedResult);

          const derivedFullName =
            `${parsedResult.firstName.latin || ""} ${
              parsedResult.lastName.latin || ""
            }`.trim() || parsedResult.fullName;

          toast.success(`Bonjour, ${derivedFullName} !.`, {
            position: "top-center",
            autoClose: 5000,
          });

          videoRecognizer.releaseVideoFeed();
          recognizerRunner.delete();
          multiSideRecognizer.delete();
          clearDrawCanvas(drawContext);
          setIsScanning(false);
          setIsLoading(false);
        });
      } catch (err) {
        setError("Erreur lors de l'initialisation du scan");
        toast.error("Erreur lors de l'initialisation du scan");
        console.error("Erreur lors du scan :", err);
        setIsScanning(false);
        setIsLoading(false);
      }
    };

    startScan();
  }, [isScanning]);

  // Nettoyage lors du démontage
  useEffect(() => {
    return () => {
      if (videoRecognizerRef.current) {
        videoRecognizerRef.current.releaseVideoFeed();
      }
      if (sdkRef.current) {
        sdkRef.current.delete();
      }
    };
  }, []);

  const parseResults = (result) => {
    return result;
  };

  const drawQuad = (quad, drawContext) => {
    clearDrawCanvas(drawContext);
    setupColor(quad, drawContext);
    setupMessage(quad);
    applyTransform(quad.transformMatrix, drawContext);
    drawContext.beginPath();
    drawContext.moveTo(quad.topLeft.x, quad.topLeft.y);
    drawContext.lineTo(quad.topRight.x, quad.topRight.y);
    drawContext.lineTo(quad.bottomRight.x, quad.bottomRight.y);
    drawContext.lineTo(quad.bottomLeft.x, quad.bottomLeft.y);
    drawContext.closePath();
    drawContext.stroke();
  };

  const applyTransform = (transformMatrix, drawContext) => {
    const canvasAR = canvasRef.current.width / canvasRef.current.height;
    const videoAR = videoRef.current.videoWidth / videoRef.current.videoHeight;
    let xOffset = 0;
    let yOffset = 0;
    let scaledVideoHeight = 0;
    let scaledVideoWidth = 0;

    if (canvasAR > videoAR) {
      scaledVideoHeight = canvasRef.current.height;
      scaledVideoWidth = videoAR * scaledVideoHeight;
      xOffset = (canvasRef.current.width - scaledVideoWidth) / 2;
    } else {
      scaledVideoWidth = canvasRef.current.width;
      scaledVideoHeight = scaledVideoWidth / videoAR;
      yOffset = (canvasRef.current.height - scaledVideoHeight) / 2;
    }

    drawContext.translate(xOffset, yOffset);
    drawContext.scale(
      scaledVideoWidth / videoRef.current.videoWidth,
      scaledVideoHeight / videoRef.current.videoHeight
    );
    drawContext.transform(
      transformMatrix[0],
      transformMatrix[3],
      transformMatrix[1],
      transformMatrix[4],
      transformMatrix[2],
      transformMatrix[5]
    );
  };

  const clearDrawCanvas = (drawContext) => {
    canvasRef.current.width = canvasRef.current.clientWidth;
    canvasRef.current.height = canvasRef.current.clientHeight;
    drawContext.clearRect(
      0,
      0,
      canvasRef.current.width,
      canvasRef.current.height
    );
  };

  const setupColor = (displayable, drawContext) => {
    let color = "#FFFF00FF";
    if (displayable.detectionStatus === 0) {
      color = "#FF0000FF";
    } else if (displayable.detectionStatus === 1) {
      color = "#00FF00FF";
    }
    drawContext.fillStyle = color;
    drawContext.strokeStyle = color;
    drawContext.lineWidth = 5;
  };

  const setupMessage = (displayable) => {
    switch (displayable.detectionStatus) {
      case BlinkIDSDK.DetectionStatus.Failed:
        updateScanFeedback("Scan en cours...");
        break;
      case BlinkIDSDK.DetectionStatus.Success:
      case BlinkIDSDK.DetectionStatus.FallbackSuccess:
        updateScanFeedback("Détection réussie");
        break;
      case BlinkIDSDK.DetectionStatus.CameraAngleTooSteep:
        updateScanFeedback("Ajustez l'angle");
        break;
      case BlinkIDSDK.DetectionStatus.CameraTooFar:
        updateScanFeedback("Rapprochez le document");
        break;
      case BlinkIDSDK.DetectionStatus.CameraTooClose:
      case BlinkIDSDK.DetectionStatus.DocumentTooCloseToCameraEdge:
      case BlinkIDSDK.DetectionStatus.DocumentPartiallyVisible:
        updateScanFeedback("Éloignez le document");
        break;
      default:
        console.warn(
          "Statut de détection non géré !",
          displayable.detectionStatus
        );
    }
  };

  const updateScanFeedback = (message, force = false) => {
    if (scanFeedbackLockRef.current && !force) return;
    scanFeedbackLockRef.current = true;
    setScanFeedback(message);
    setTimeout(() => (scanFeedbackLockRef.current = false), 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Oui - Scan Webcam ID</title>
        <meta name="description" content="Scannez votre ID avec votre webcam" />
      </Head>

      <main className="container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold text-center mb-8">
          Scannez Votre CNI avec la Webcam (Recto et Verso)
        </h1>

        <div className="max-w-4xl mx-auto space-y-8">
          {!isScanning && (
            <button
              onClick={() => {
                setIsLoading(true);
                setIsScanning(true);
              }}
              disabled={isLoading}
              className={`px-6 py-3 rounded-lg w-full font-medium text-white ${
                isLoading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              } transition-colors`}
            >
              {isLoading ? "Chargement..." : "Démarrer le Scan"}
            </button>
          )}

          <div className={`relative ${!isScanning ? "hidden" : ""}`}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full rounded-lg"
            />
            <canvas
              ref={canvasRef}
              className="absolute top-0 left-0 w-full h-full"
            />
            <p className="text-center mt-4 text-lg">{scanFeedback}</p>
          </div>

          {isMounted && processingResult && (
            <OcrIdVerificationResult processingResult={processingResult} />
          )}

          {error && (
            <div className="p-4 bg-red-100 text-red-700 rounded-lg">
              ❌ Erreur : {error}
            </div>
          )}
        </div>
      </main>
      <ToastContainer position="top-right" theme="light" />
    </div>
  );
}
