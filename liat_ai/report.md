# Player Re-Identification in Sports Footage - Assignment Report

**Author:** Vaishnav Mankar

**Task:** Re-Identification in a Single Feed

---

## 1. Objective

The goal of this task was to perform player re-identification on a 15-second video clip (`15sec_input_720p.mp4`). The primary challenge was to ensure that any player who leaves the camera's field of view and later reappears is assigned their original, consistent ID. This required implementing a robust tracking solution that combines object detection with an appearance-based re-identification mechanism.

## 2. Methodology & Approach

My strategy was to leverage the powerful, pre-built tools from the Ultralytics library while critically analyzing their performance and limitations in this specific sports analytics context.

### Step 1: Baseline Detection and Tracking

The foundation of the solution is the object detection model provided in the assignment (`yolov11n` fine-tuned for players and the ball). I used this model to detect all players in each frame of the video. For tracking, I selected the **BoT-SORT** algorithm, which integrates both motion prediction and appearance features.

### Step 2: Enabling and Testing the Re-Identification Module

My core approach was to utilize BoT-SORT's built-in re-identification capabilities.

1.  **Activation:** I modified the tracker's configuration file (`botsort.yaml`) to set `with_reid: True`. This activates the appearance-based matching feature, which is essential for this task.

2.  **Experimentation:** I experimented with key parameters, particularly `reid_cos_dist`, to understand their impact. However, no amount of tuning could overcome the fundamental challenge presented in the video. The final submitted version uses the most stable configuration I found, which was [e.g., the default `with_reid: True` settings].

## 3. Results & Demonstration

The implemented solution offers two distinct levels of performance:

*   **Continuous Tracking:** The system is highly effective at maintaining stable, consistent IDs for all players who remain within the camera's view or are only briefly occluded. This provides a solid baseline for short-term tracking.

*   **Long-Term Re-Identification:** The provided video contains one critical event where a player exits the frame and returns after several seconds. This event serves as the definitive test for the re-identification module. **In this key scenario, the system fails to re-identify the player.**


### Analysis of the Key Re-Identification Event

This single event perfectly encapsulates the core challenge of the assignment.

[![Demonstration of Re-ID Failure](output_video/output_tracked_video.gif)](output_video/output_tracked_video.mp4)

**(Click the animation below to see the full video with controls)**

**Observation:**
1.  A player is correctly assigned an initial ID (e.g., ID #7).
2.  The player runs out of the right side of the frame.
3.  Upon re-entering the frame near the goal, the tracker fails to match their appearance to the "lost" track of ID #7 and instead assigns a new ID (e.g., ID #15).

This **failure** demonstrates that the default appearance-embedding model used by BoT-SORT is not sufficiently discriminative for this sports-specific use case. The visual similarity between players (identical uniforms, similar builds) confuses the model, causing it to treat the returning player as a new entity.

## 4. Challenges Encountered

The primary challenge is not a bug in the code, but a fundamental limitation of the tool being used.

*   **Critical Lack of Differentiating Features:** The generic Re-ID model struggles when every target shares the same primary color and shape (the team uniform). It is unable to learn the subtle, unique features (e.g., face, running gait, cleats) needed to tell players apart.
*   **The "Single Point of Failure":** With only one major re-identification event in the clip, the success of the entire task hinged on this moment. The failure is therefore not just a minor error but a complete breakdown of the long-term tracking goal.

## 5. Incomplete Aspects & Future Work

The current solution is an excellent diagnostic tool but is not a robust re-identification system. The analysis of its failure points directly to the necessary future work.

Given more time, the clear, methodical path to a production-grade solution is to **build a custom Re-ID model**:

1.  **Create a Custom Dataset:** Manually crop images of each individual player from the video. Even a small dataset (20-30 images per player) would be a powerful start.
2.  **Fine-Tune a Specialized Network:** Use a proven person Re-ID architecture, such as **OSNet**, pre-trained on a large public dataset. Fine-tune this network on the custom player dataset. This will force the model to learn the minor visual cues that differentiate the players, rather than just looking at uniform color.
3.  **Integrate the Custom Model:** Swap out the default Re-ID logic in the tracking loop. When a new player appears, their appearance embedding would be generated by the custom-trained OSNet model and compared against a gallery of lost tracks, ensuring a much higher probability of an accurate match.

This approach directly tackles the root cause of the failure observed and represents the standard industry practice for solving such domain-specific problems.