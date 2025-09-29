# Google Summer of Code (GSoC) 2025 TV News Archive Social Media Mentions project
By: Himarsha R. Jayanetti  
Last update: September 28, 2025

More: [Blog post](https://ws-dl.blogspot.com/2025/09/2025-09-29-summer-project-as-google.html)

## Problem

Information diffusion in social media has been well studied.  For example, social and political scientists have tracked how social movements like #MeToo spread on social media and estimated political leanings of social media users.  But one area that has yet to be studied is the reference of social media in conventional broadcast television news. 

## Solution

Our study addresses this gap by analyzing TV news broadcasts for references to social media. We focused on the detection of visual representations, such as social media platform logos and screenshots of user posts in TV news. Using sampled primetime episodes from CNN, Fox News, and MSNBC (2020–2024), we built a gold standard dataset of annotated frames and implemented an automated detection system by using the ChatGPT-4o multimodal API. The workflow included preprocessing video frames with perceptual hashing to reduce redundancy, iterative prompt engineering to improve detection accuracy, and evaluation against manually labeled gold standard data. Results showed strong performance for screenshot detection and iterative improvements for logo detection, especially with refined prompts. 

## The current state

Prompt versions: [Prompt version 1-7](https://github.com/internetarchive/tvnews_socialmedia_mentions/commits/main/LLMs/Prompt)

Final prompt version: [Prompt version 7](https://github.com/internetarchive/tvnews_socialmedia_mentions/blob/f0eb824d729e1727bc8b748066cee2ad87b911fc/LLMs/Prompt/prompt.md)

The current results from the final prompt configuration (Prompt version 7) are summarized in the tables below.  

Logo detection:
| Channel  | Accuracy | Precision | Recall  | F1-score |
|----------|----------|-----------|---------|----------|
| CNN      | 0.9965   | 0.3529    | 0.8889  | 0.5053   |
| FOX News | 0.9926   | 0.5963    | 0.8298  | 0.6940   |
| MSNBC    | 0.9980   | 0.8535    | 0.9306  | 0.8904   |


Screenshot detection:
| Channel  | Accuracy | Precision | Recall  | F1-score |
|----------|----------|-----------|---------|----------|
| CNN      | 0.9986   | 0.5789    | 0.8800  | 0.6984   |
| FOX News | 0.9945   | 0.2456    | 1.0000  | 0.3944   |
| MSNBC    | 0.9988   | 0.8496    | 0.9697  | 0.9057   |


## What's left to do

Several directions remain for extending this work:

- **Prompt Refinement and Channel-Specific Tuning:**  
  We will continue refining the analysis prompt to increase accuracy and consistency in detecting social media logos and user post screenshots. Early observations suggest that performance varies across channels (and programs), likely due to unique ways in which social media is visually presented. This indicates that channel- or program-specific prompt tuning could further enhance results.

- **Decoding Temperature Exploration:**  
  While our experiments primarily used low decoding temperatures (0.0 and 0.2), future work can explore a range of temperatures to evaluate whether controlled increases in randomness improve recall in edge cases without significantly raising false positives.

- **Frame Selection Strategies:**  
  Preliminary observations using different Hamming distance thresholds (t=5,4,3) were conducted to group similar frames and experiment with selecting the first, middle, or last frame from each group. Future work will investigate the effects of different frame selection strategies to reduce redundancy without losing relevant content.

- **Confidence Scores:**  
  Confidence scores for logos and screenshots (ranging from 0 to 1) were recorded but not yet utilized. Future work will explore integrating these scores into the analysis to weigh detections and potentially improve precision.

- **Dataset Expansion:**  
  Manually labeling additional episodes from multiple days of prime-time TV news will expand the gold standard dataset, uncovering more instances of social media references. This will also allow evaluation of detection performance across diverse broadcast content.

- **Advertisement Filtering:**  
  With access to advertisement segments, ad images can be excluded before evaluation. This will improve results, as currently, the pipeline includes ads, leading to some apparent false positives that are actually correct detections.

- **Complementary Detection Methods:**  
  Future work will focus on approaches beyond logo and screenshot detection, such as analyzing OCR-extracted text from video frames and closed-caption transcripts for social media references.

- **Compare Against Other Multimodal Models:**  
  We aim to explore other vision-language APIs, such as Google’s Gemini Pro, to compare detection performance across different Large Language Models (LLMs).

## Acknowledgements

I sincerely thank the [Internet Archive](https://archive.org/) and the [Google Summer of Code Program](https://summerofcode.withgoogle.com/) for providing this amazing opportunity. Specially, I would like to thank [Sawood Alam](https://www.linkedin.com/in/ibnesayeed/), Research Lead, and [Will Howes](https://www.linkedin.com/in/will-howes-269b5a175/), Software Engineer, at the Internet Archive’s Wayback Machine for their guidance and mentorship. I also acknowledge [Mark Graham](https://www.linkedin.com/in/markjohngraham/), Director of the Wayback Machine at the Internet Archive and [Roger Macdonald](https://x.com/r_macdonald), Founder of the Internet Archive’s TV News Archive for their invaluable support.  I am grateful to the [TV News Archive](https://archive.org/details/tv) team for welcoming me into their meetings during the summer, which allowed me to gain a deeper understanding of the archive and its work. I am especially grateful to [Kalev Leetaru](https://www.linkedin.com/in/kalevleetaru/) (Founder, the GDELT Project) for providing the necessary Internet Archive data which were processed through the GDELT project. Finally, I would like to thank my PhD advisors, [Dr. Michele Weigle] and [Dr. Michael Nelson] (Old Dominion University) and [Dr. Alexander Nwala] (William & Mary) for their continued guidance.
