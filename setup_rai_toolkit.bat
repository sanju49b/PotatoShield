@echo off
REM Setup script for Infosys Responsible AI Toolkit integration (Windows)
REM Run this script to clone and install all RAI modules

echo ==================================================
echo Infosys Responsible AI Toolkit Setup
echo For Potato Shield - UK-India AIxcelerate 2025-26
echo ==================================================
echo.

REM Step 1: Clone the Infosys RAI Toolkit repository
echo [1/8] Cloning Infosys Responsible AI Toolkit...
if not exist "rai-toolkit" (
    git clone https://github.com/Infosys/Infosys-Responsible-AI-Toolkit.git rai-toolkit
    echo ✅ RAI Toolkit cloned successfully
) else (
    echo ⚠️  RAI Toolkit directory already exists. Skipping clone.
)
echo.

REM Step 2: Install ModerationLayer API
echo [2/8] Installing ModerationLayer API...
cd rai-toolkit\responsible-ai-moderationlayer
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ ModerationLayer dependencies installed
) else (
    echo ⚠️  requirements.txt not found in moderationlayer
)
cd ..\..
echo.

REM Step 3: Install Hallucination Detection API
echo [3/8] Installing Hallucination Detection API...
cd rai-toolkit\responsible-ai-Hallucination
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Hallucination API dependencies installed
) else (
    echo ⚠️  requirements.txt not found in Hallucination module
)
cd ..\..
echo.

REM Step 4: Install Privacy API
echo [4/8] Installing Privacy API...
cd rai-toolkit\responsible-ai-privacy
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Privacy API dependencies installed
) else (
    echo ⚠️  requirements.txt not found in privacy module
)
cd ..\..
echo.

REM Step 5: Install Safety API
echo [5/8] Installing Safety API...
cd rai-toolkit\responsible-ai-safety
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Safety API dependencies installed
) else (
    echo ⚠️  requirements.txt not found in safety module
)
cd ..\..
echo.

REM Step 6: Install Fairness API
echo [6/8] Installing Fairness API...
cd rai-toolkit\responsible-ai-fairness
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Fairness API dependencies installed
) else (
    echo ⚠️  requirements.txt not found in fairness module
)
cd ..\..
echo.

REM Step 7: Install Explainability API
echo [7/8] Installing Explainability API...
cd rai-toolkit\responsible-ai-llm-explain
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Explainability API dependencies installed
) else (
    echo ⚠️  requirements.txt not found in llm-explain module
)
cd ..\..
echo.

REM Step 8: Install RAI Backend
echo [8/8] Installing RAI Backend...
cd rai-toolkit\responsible-ai-backend
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ RAI Backend dependencies installed
) else (
    echo ⚠️  requirements.txt not found in backend module
)
cd ..\..
echo.

echo ==================================================
echo ✅ Infosys RAI Toolkit installation complete!
echo ==================================================
echo.
echo Next steps:
echo 1. Configure RAI endpoints in config\rai_config.yaml
echo 2. Start RAI Backend service: cd rai-toolkit\responsible-ai-backend ^&^& python app.py
echo 3. Run integration tests: python test_rai_integration.py
echo 4. Start Potato Shield with RAI: python api\main.py
echo.
pause
