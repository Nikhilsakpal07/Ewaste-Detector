document.addEventListener("DOMContentLoaded", () => {
    gsap.registerPlugin(ScrollTrigger);

    // Custom Cursor
    const cursor = document.getElementById("cursor");
    const follower = document.getElementById("cursor-follower");
    document.addEventListener("mousemove", (e) => {
        gsap.to(cursor, { x: e.clientX, y: e.clientY, duration: 0.1 });
        gsap.to(follower, { x: e.clientX, y: e.clientY, duration: 0.3 });
    });

    // 3D Tilt Effect for cards
    const tiltCards = document.querySelectorAll(".tilt-card");
    tiltCards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const xPct = x / rect.width - 0.5;
            const yPct = y / rect.height - 0.5;
            gsap.to(card, {
                rotationY: xPct * 15,
                rotationX: -yPct * 15,
                transformPerspective: 1000,
                ease: "power1.out",
                duration: 0.5
            });
        });
        card.addEventListener("mouseleave", () => {
            gsap.to(card, { rotationY: 0, rotationX: 0, duration: 0.5, ease: "power1.out" });
        });
    });

    // (Live E-Waste Counter removed as requested)

    // Random Hex Generator for HUD
    const hexEl = document.getElementById("random-hex");
    const dataStreamEl = document.getElementById("data-stream");
    setInterval(() => {
        const hex = () => "0x" + Math.floor(Math.random()*65535).toString(16).toUpperCase().padStart(4, '0');
        if(hexEl) hexEl.innerText = `${hex()} ${hex()} ${hex()}`;
        
        if(Math.random() > 0.7) {
            const streams = [
                "Analyzing binary structures...",
                "Scanning memory blocks...",
                "Waiting for neural network...",
                "Processing pixel matrices...",
                "Allocating tensors..."
            ];
            dataStreamEl.innerText = streams[Math.floor(Math.random() * streams.length)];
        }
    }, 500);

    // Clock
    const clockEl = document.getElementById("hud-clock");
    setInterval(() => {
        const d = new Date();
        clockEl.innerText = d.toISOString().split('T')[1].split('.')[0] + " UTC";
    }, 1000);

    // Scroll Animations
    const tlHero = gsap.timeline();
    tlHero.from(".navbar", { y: -50, opacity: 0, duration: 1, ease: "power3.out" })
          .from(".hero-content h1", { x: -50, opacity: 0, duration: 1, ease: "power3.out" }, "-=0.5")
          .from(".hero-content p", { x: -50, opacity: 0, duration: 1, ease: "power3.out" }, "-=0.8")
          .from(".hero-actions", { y: 20, opacity: 0, duration: 1, ease: "power3.out" }, "-=0.8")
          .from(".hero-graphic", { scale: 0.8, opacity: 0, duration: 1, ease: "power3.out" }, "-=1");

    gsap.to(".floating-chip", { y: -15, duration: 2, yoyo: true, repeat: -1, ease: "sine.inOut" });
    gsap.to(".chip-2", { y: 15, duration: 2.5, yoyo: true, repeat: -1, ease: "sine.inOut" });

    // Scrub animations
    const cards = gsap.utils.toArray(".feature-card");
    cards.forEach((card, i) => {
        gsap.fromTo(card, 
            { y: 100, opacity: 0 },
            { 
                scrollTrigger: { trigger: card, start: "top 90%", end: "top 60%", scrub: 1 },
                y: 0, opacity: 1, ease: "power2.out"
            }
        );
    });

    gsap.fromTo(".split-text", 
        { x: -100, opacity: 0 },
        { scrollTrigger: { trigger: ".impact-section", start: "top 85%", end: "top 50%", scrub: 1 }, x: 0, opacity: 1, ease: "power2.out" }
    );

    gsap.fromTo(".split-stats .stat-card", 
        { x: 100, opacity: 0 },
        { scrollTrigger: { trigger: ".impact-section", start: "top 85%", end: "top 50%", scrub: 1 }, x: 0, opacity: 1, stagger: 0.2, ease: "power2.out" }
    );

    gsap.fromTo(".app-section .panel", 
        { y: 100, opacity: 0 },
        { scrollTrigger: { trigger: ".app-section", start: "top 90%", end: "top 60%", scrub: 1 }, y: 0, opacity: 1, stagger: 0.2, ease: "power2.out" }
    );

    // App Logic
    const btnLive = document.getElementById("btn-live");
    const btnUpload = document.getElementById("btn-upload");
    const liveView = document.getElementById("live-view");
    const uploadView = document.getElementById("upload-view");
    
    // Upload Elements
    const uploadBox = document.getElementById("upload-box");
    const fileInput = document.getElementById("file-input");
    const previewContainer = document.querySelector(".preview-container");
    const imagePreview = document.getElementById("image-preview");
    const btnResetUpload = document.getElementById("btn-reset-upload");
    const videoFeed = document.getElementById("video-feed");

    const btnTriggerFile = document.getElementById("btn-trigger-file");
    const btnTriggerWebcam = document.getElementById("btn-trigger-webcam");
    const webcamBox = document.getElementById("webcam-box");
    const webcamVideo = document.getElementById("webcam-video");
    const btnCaptureWebcam = document.getElementById("btn-capture-webcam");
    const btnCancelWebcam = document.getElementById("btn-cancel-webcam");
    const webcamCanvas = document.getElementById("webcam-canvas");

    const elClass = document.getElementById("detected-class");
    const elConf = document.getElementById("detected-conf");
    const elValue = document.getElementById("detected-value");
    const elHazardBadge = document.getElementById("hazard-badge");
    const elHazardWarningCard = document.getElementById("hazard-warning-card");
    const elHazardText = document.getElementById("hazard-text");
    const elImpact = document.getElementById("detected-impact");

    const locatorCard = document.getElementById("locator-card");
    const btnLocate = document.getElementById("btn-locate");
    const locatorStatus = document.getElementById("locator-status");

    let liveInterval = null;
    let isLiveMode = true;
    let currentClass = "None";

    btnLocate.addEventListener("click", () => {
        locatorStatus.innerText = "Accessing Geolocation...";
        
        const getQuery = () => {
            const specificItems = ["Battery", "Smartphone", "Laptop", "CRT Monitor", "CRT-Monitor", "CRT-TV"];
            if (specificItems.includes(currentClass)) {
                return `${currentClass.replace('-', ' ')} recycling`;
            }
            return "e-waste recycling";
        };

        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition((position) => {
                locatorStatus.innerText = "Coordinates acquired. Routing to Maps...";
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(getQuery())}/@${lat},${lng},12z`;
                window.open(mapsUrl, "_blank");
                
                setTimeout(() => { locatorStatus.innerText = ""; }, 3000);
            }, (error) => {
                locatorStatus.innerText = "Location access denied. Opening general search.";
                window.open(`https://www.google.com/maps/search/${encodeURIComponent(getQuery() + " near me")}`, "_blank");
            });
        } else {
            locatorStatus.innerText = "Geolocation not supported.";
            window.open(`https://www.google.com/maps/search/${encodeURIComponent(getQuery() + " near me")}`, "_blank");
        }
    });

    function startLivePolling() {
        if (liveInterval) clearInterval(liveInterval);
        liveInterval = setInterval(() => {
            if (!isLiveMode) return;
            fetch("/api/latest_detection")
                .then(res => res.json())
                .then(data => updateAnalytics(data))
                .catch(err => console.error("Polling error", err));
        }, 1000);
    }

    function stopLivePolling() {
        if (liveInterval) {
            clearInterval(liveInterval);
            liveInterval = null;
        }
    }

    const liveVideo = document.createElement("video");
    liveVideo.autoplay = true;
    liveVideo.playsInline = true;
    const liveCanvas = document.createElement("canvas");
    let liveStream = null;
    let liveFeedInterval = null;

    btnLive.addEventListener("click", () => {
        if (isLiveMode) return;
        isLiveMode = true;
        btnLive.classList.add("active");
        btnUpload.classList.remove("active");
        
        uploadView.classList.remove("active");
        liveView.classList.add("active");
        
        resetAnalytics();
        
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(stream => {
                liveStream = stream;
                liveVideo.srcObject = stream;
                liveVideo.play();
                
                liveFeedInterval = setInterval(() => {
                    if (liveVideo.videoWidth === 0) return;
                    liveCanvas.width = liveVideo.videoWidth;
                    liveCanvas.height = liveVideo.videoHeight;
                    liveCanvas.getContext("2d").drawImage(liveVideo, 0, 0);
                    liveCanvas.toBlob(blob => {
                        const formData = new FormData();
                        formData.append("image", new File([blob], "frame.jpg", { type: "image/jpeg" }));
                        
                        fetch("/api/analyze_frame_yolo", { method: "POST", body: formData })
                            .then(res => res.json())
                            .then(data => {
                                if (data.error) {
                                    console.error(data.error);
                                    if(isLiveMode) {
                                        elClass.innerText = "SYS_ERROR";
                                        elImpact.innerText = data.error;
                                    }
                                    return;
                                }
                                if(isLiveMode) {
                                    videoFeed.src = data.image;
                                    updateAnalytics(data.info, false);
                                }
                            }).catch(err => console.error(err));
                    }, "image/jpeg", 0.7);
                }, 500);
            })
            .catch(err => {
                console.error("Camera error:", err);
                alert("Please allow camera access for the Live Feed.");
            });
    });

    btnUpload.addEventListener("click", () => {
        if (!isLiveMode) return;
        isLiveMode = false;
        btnUpload.classList.add("active");
        btnLive.classList.remove("active");
        
        liveView.classList.remove("active");
        uploadView.classList.add("active");
        
        videoFeed.src = "";
        
        if (liveFeedInterval) clearInterval(liveFeedInterval);
        if (liveStream) {
            liveStream.getTracks().forEach(t => t.stop());
            liveStream = null;
        }
        resetAnalytics();
    });

    btnTriggerFile.addEventListener("click", (e) => { e.stopPropagation(); fileInput.click(); });

    let browserStream = null;

    btnTriggerWebcam.addEventListener("click", (e) => {
        e.stopPropagation();
        uploadBox.style.display = "none";
        webcamBox.style.display = "flex";
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(stream => {
                browserStream = stream;
                webcamVideo.srcObject = stream;
            })
            .catch(err => {
                console.error("Webcam error:", err);
                alert("Could not access webcam. Please check permissions.");
                cancelBrowserWebcam();
            });
    });

    function cancelBrowserWebcam() {
        if (browserStream) {
            browserStream.getTracks().forEach(track => track.stop());
            browserStream = null;
        }
        webcamBox.style.display = "none";
        uploadBox.style.display = "flex";
    }

    btnCancelWebcam.addEventListener("click", cancelBrowserWebcam);

    btnCaptureWebcam.addEventListener("click", () => {
        if (!browserStream) return;
        webcamCanvas.width = webcamVideo.videoWidth;
        webcamCanvas.height = webcamVideo.videoHeight;
        const ctx = webcamCanvas.getContext("2d");
        ctx.drawImage(webcamVideo, 0, 0, webcamCanvas.width, webcamCanvas.height);
        
        webcamCanvas.toBlob(blob => {
            const file = new File([blob], "snapshot.jpg", { type: "image/jpeg" });
            cancelBrowserWebcam();
            uploadBox.style.display = "none";
            previewContainer.style.display = "flex";
            imagePreview.src = URL.createObjectURL(file);
            processImageFile(file);
        }, "image/jpeg", 0.9);
    });

    fileInput.addEventListener("change", handleFileUpload);

    btnResetUpload.addEventListener("click", () => {
        previewContainer.style.display = "none";
        uploadBox.style.display = "flex";
        fileInput.value = "";
        resetAnalytics();
    });

    function handleFileUpload() {
        if (!fileInput.files.length) return;
        const file = fileInput.files[0];
        uploadBox.style.display = "none";
        previewContainer.style.display = "flex";
        imagePreview.src = URL.createObjectURL(file);
        processImageFile(file);
    }

    function processImageFile(file) {
        elClass.innerText = "ANALYZING_MATRIX";
        elImpact.innerText = "Extracting hazard vectors via YOLOv8 and Gemini AI...";
        dataStreamEl.innerText = "[ PROCESSING IMAGE_FILE_01 ]";
        
        const formData = new FormData();
        formData.append("image", file);

        fetch("/api/analyze_image", { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error(data.traceback || data.error);
                elClass.innerText = "SYS_ERROR";
                elImpact.innerText = `CRASH: ${data.error}`;
                return;
            }
            imagePreview.src = data.image; 
            updateAnalytics(data.info, true);
        })
        .catch(err => {
            console.error(err);
            elClass.innerText = "SYS_ERROR";
            elImpact.innerText = "Network Error: Could not connect to the cloud server. It may have crashed due to memory limits.";
        });
    }

    function resetAnalytics() {
        elClass.innerText = "AWAITING...";
        elClass.style.color = "var(--primary)";
        elConf.innerText = "0.00%";
        elValue.innerText = "₹0";
        elImpact.innerText = isLiveMode ? "System idle. Waiting for hardware target..." : "Upload an image to execute scan.";
        
        elHazardBadge.classList.remove("danger");
        elHazardBadge.querySelector(".icon").innerText = "✅";
        elHazardBadge.querySelector(".text").innerText = "SECURE";
        elHazardWarningCard.style.display = "none";
        locatorCard.style.display = "none";
        locatorStatus.innerText = "";
        currentClass = "None";
    }

    function updateAnalytics(info, forceAnimate = false) {
        if (!info) return;

        const shouldAnimate = forceAnimate || currentClass !== info.class;
        currentClass = info.class;

        if (info.class === "None") {
            elClass.innerText = "SCANNING...";
            elClass.style.color = "var(--primary)";
            elConf.innerText = "0.00%";
            elValue.innerText = "₹0";
            if(elImpact.innerText !== "Checking Gemini AI...") {
                 elImpact.innerText = "Scanning environment for e-waste...";
            }
            elHazardBadge.classList.remove("danger");
            elHazardBadge.querySelector(".icon").innerText = "✅";
            elHazardBadge.querySelector(".text").innerText = "SECURE";
            elHazardWarningCard.style.display = "none";
            locatorCard.style.display = "none";
            locatorStatus.innerText = "";
            return;
        }

        elClass.innerText = info.class.toUpperCase();
        elConf.innerText = info.confidence + "%";
        elValue.innerText = info.value;
        
        if (info.impact) {
            elImpact.innerText = info.impact;
        }

        dataStreamEl.innerText = `[ MATCH_FOUND: ${info.class.toUpperCase()} @ ${info.confidence}% ]`;

        if (info.hazard) {
            elClass.style.color = "var(--hazard)";
            elHazardBadge.classList.add("danger");
            elHazardBadge.querySelector(".icon").innerText = "☣️";
            elHazardBadge.querySelector(".text").innerText = "HAZARD";
            
            elHazardWarningCard.style.display = "block";
            elHazardText.innerText = info.hazard_text;
        } else {
            elClass.style.color = "var(--primary)";
            elHazardBadge.classList.remove("danger");
            elHazardBadge.querySelector(".icon").innerText = "✅";
            elHazardBadge.querySelector(".text").innerText = "SECURE";
            
            elHazardWarningCard.style.display = "none";
        }

        // Show locator button only when something is detected
        locatorCard.style.display = "block";

        if (shouldAnimate) {
            gsap.from([elClass, elValue, elImpact], {
                y: 10,
                opacity: 0.5,
                duration: 0.2,
                stagger: 0.1,
                ease: "power2.out"
            });
        }
    }

    // --- Mobile Link Logic ---
    const btnMobileConnect = document.getElementById("btn-mobile-connect");
    const mobileModal = document.getElementById("mobile-modal");
    const qrCode = document.getElementById("qr-code");
    const btnCloseModal = document.getElementById("btn-close-modal");

    if (btnMobileConnect && mobileModal) {
        btnMobileConnect.addEventListener("click", (e) => {
            e.preventDefault();
            const url = window.location.origin + '/mobile';
            qrCode.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(url)}&bgcolor=FFFFFF`;
            mobileModal.style.display = "flex";
        });

        btnCloseModal.addEventListener("click", () => {
            mobileModal.style.display = "none";
        });
    }

    // --- Inventory Logic ---
    const btnInventory = document.getElementById("btn-inventory");
    const inventoryModal = document.getElementById("inventory-modal");
    const btnCloseInventory = document.getElementById("btn-close-inventory");
    const inventoryContainer = document.getElementById("inventory-container");

    if (btnInventory && inventoryModal) {
        btnInventory.addEventListener("click", (e) => {
            e.preventDefault();
            inventoryModal.style.display = "flex";
            loadInventory();
        });
        btnCloseInventory.addEventListener("click", () => {
            inventoryModal.style.display = "none";
        });
    }

    function loadInventory() {
        inventoryContainer.innerHTML = '<p style="text-align: center; color: var(--text-muted); font-style: italic;">Loading inventory records...</p>';
        fetch('/api/inventory')
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                inventoryContainer.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 50px;">No E-Waste records found in mainframe.</p>';
                return;
            }
            
            let html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px;">';
            data.forEach(item => {
                const info = item.info;
                const hazardStyle = info.hazard ? 'border-color: var(--hazard);' : '';
                const hazardBadge = info.hazard ? `<div style="color: var(--hazard); font-size: 0.8rem; font-weight: bold; margin-bottom: 10px;">⚠️ HAZARDOUS</div>` : '';
                
                html += `
                    <div class="card-glass" style="padding: 15px; display: flex; flex-direction: column; gap: 10px; ${hazardStyle}">
                        <img src="${item.image_url}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);" />
                        <div>
                            <h3 style="color: var(--primary); margin-bottom: 5px; font-family: 'Share Tech Mono';">${info.class.toUpperCase()}</h3>
                            <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 10px;">${item.timestamp}</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #C3E88D; margin-bottom: 10px;">${info.value}</div>
                            ${hazardBadge}
                            <p style="font-size: 0.85rem; color: var(--text-muted); height: 80px; overflow-y: auto;">${info.impact}</p>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            inventoryContainer.innerHTML = html;
        })
        .catch(err => {
            inventoryContainer.innerHTML = '<p style="text-align: center; color: var(--hazard);">Failed to load inventory.</p>';
        });
    }

    // Polling for Desktop Sync from Mobile Uploads
    setInterval(() => {
        fetch("/api/desktop_sync")
        .then(res => res.json())
        .then(data => {
            if(data.has_new) {
                // Switch to upload view
                btnUpload.click();
                previewContainer.style.display = "flex";
                uploadBox.style.display = "none";
                imagePreview.src = data.data.image;
                
                elClass.innerText = "MOBILE SYNCING...";
                elClass.style.color = "var(--hazard)";
                dataStreamEl.innerText = "[ INCOMING MOBILE DATA... ]";
                
                setTimeout(() => {
                    updateAnalytics(data.data.info, true);
                }, 1000);
            }
        })
        .catch(err => {});
    }, 2000);

    startLivePolling();
});
