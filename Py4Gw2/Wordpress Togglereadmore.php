// Move the helper function outside and give it a unique name
function get_text_nodes_for_additional_info($node, &$textNodes) {
    if ($node->nodeType === XML_TEXT_NODE) {
        $text = trim($node->nodeValue);
        if (!empty($text)) {
            $textNodes[] = $node;
        }
    }
    if ($node->hasChildNodes()) {
        foreach ($node->childNodes as $child) {
            get_text_nodes_for_additional_info($child, $textNodes);
        }
    }
}

// Rename the main content filter function
function filter_the_content_readmore($content) {
    // Only for single product pages
    if (!is_product()) return $content;

    // Set the limit of words
    $limit = 25;
    
    // Create a DOMDocument instance
    $dom = new DOMDocument();
    // Prevent HTML5 errors
    libxml_use_internal_errors(true);
    $dom->loadHTML(mb_convert_encoding($content, 'HTML-ENTITIES', 'UTF-8'), LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
    libxml_clear_errors();

    // Clone the DOM for the second part
    $fullDom = clone $dom;
    
    // Get all text nodes
    $textNodes = array();
    $words = array();
    
    get_text_nodes_for_additional_info($dom->documentElement, $textNodes);
    
    // Count total words
    foreach ($textNodes as $node) {
        $nodeWords = preg_split('/\s+/', trim($node->nodeValue));
        $words = array_merge($words, array_filter($nodeWords));
    }

    // If the content is longer than the predetermined limit
    if (count($words) > $limit) {
        $wordCount = 0;
        // Modify first part to show only limited words
        foreach ($textNodes as $node) {
            $nodeWords = preg_split('/\s+/', trim($node->nodeValue));
            $nodeWords = array_filter($nodeWords);
            
            if ($wordCount + count($nodeWords) <= $limit) {
                $wordCount += count($nodeWords);
            } else {
                $remainingWords = $limit - $wordCount;
                $node->nodeValue = implode(' ', array_slice($nodeWords, 0, $remainingWords));
                // Remove nodes after this one
                $nextNode = $node->nextSibling;
                while ($nextNode) {
                    $temp = $nextNode->nextSibling;
                    $nextNode->parentNode->removeChild($nextNode);
                    $nextNode = $temp;
                }
                break;
            }
        }

        // Get the HTML content for both parts
        $first_part = $dom->saveHTML();
        $second_part = $fullDom->saveHTML();
        
        // Modify to only show the full content in the more-text section
        $content = '
            <div class="product-description">
                <div class="preview-text">' . $first_part . '</div>
                <span class="dots">...</span>
                <div class="more-text" style="display: none;">' . $second_part . '</div>
                <button onclick="toggleReadMore(this)" class="read-more-btn">Read more</button>
            </div>
        ';
        
        // Update the JavaScript
        add_action('wp_footer', function() {
            ?>
            <script>
            function toggleReadMore(btn) {
                var parent = btn.closest('.product-description');
                var moreText = parent.querySelector('.more-text');
                var previewText = parent.querySelector('.preview-text');
                var dots = parent.querySelector('.dots');
                
                if (moreText.style.display === "none") {
                    // When expanding
                    dots.style.display = "none";
                    previewText.style.display = "none";  // Ensure this is actually hiding
                    moreText.style.display = "inline";   // Changed to inline from block
                    btn.textContent = "Read less";
                } else {
                    // When collapsing
                    dots.style.display = "inline";
                    previewText.style.display = "block";
                    moreText.style.display = "none";
                    btn.textContent = "Read more";
                }
            }
            </script>
            <style>
            .product-description .more-text {
                display: none;
            }
            .read-more-btn {
                margin-top: 10px;
                cursor: pointer;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                padding: 5px 15px;
                border-radius: 4px;
            }
            .read-more-btn:hover {
                background-color: #e0e0e0;
            }
            .dots {
                display: inline;
            }
            </style>
            <?php
        }, 99);
    }
    
    return $content;
}
// Update the filter hook to use the new function name
add_filter('the_content', 'filter_the_content_readmore', 10, 1);

function filter_additional_information($content) {
    // Only for single product pages
    if (!is_product()) return $content;

    // Set the limit of words
    $limit = 25;
    
    // Create a DOMDocument instance
    $dom = new DOMDocument();
    // Prevent HTML5 errors
    libxml_use_internal_errors(true);
    $dom->loadHTML(mb_convert_encoding($content, 'HTML-ENTITIES', 'UTF-8'), LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
    libxml_clear_errors();

    // Clone the DOM for the second part
    $fullDom = clone $dom;
    
    // Get all text nodes
    $textNodes = array();
    $words = array();
    
    get_text_nodes_for_additional_info($dom->documentElement, $textNodes);
    
    // Count total words
    foreach ($textNodes as $node) {
        $nodeWords = preg_split('/\s+/', trim($node->nodeValue));
        $words = array_merge($words, array_filter($nodeWords));
    }

    // If the content is longer than the predetermined limit
    if (count($words) > $limit) {
        $wordCount = 0;
        // Modify first part to show only limited words
        foreach ($textNodes as $node) {
            $nodeWords = preg_split('/\s+/', trim($node->nodeValue));
            $nodeWords = array_filter($nodeWords);
            
            if ($wordCount + count($nodeWords) <= $limit) {
                $wordCount += count($nodeWords);
            } else {
                $remainingWords = $limit - $wordCount;
                $node->nodeValue = implode(' ', array_slice($nodeWords, 0, $remainingWords));
                // Remove nodes after this one
                $nextNode = $node->nextSibling;
                while ($nextNode) {
                    $temp = $nextNode->nextSibling;
                    $nextNode->parentNode->removeChild($nextNode);
                    $nextNode = $temp;
                }
                break;
            }
        }

        // Get the HTML content for both parts
        $first_part = $dom->saveHTML();
        $second_part = $fullDom->saveHTML();
        
        // Modify to only show the full content in the more-text section
        $content = '
            <div class="product-additional-information">
                <div class="preview-text-info">' . $first_part . '</div>
                <span class="dots-info">...</span>
                <div class="more-text-info" style="display: none;">' . $second_part . '</div>
                <button onclick="toggleReadMoreInfo(this)" class="read-more-btn-info">Read more</button>
            </div>
        ';
        
        // Update the JavaScript with new function name and selectors
        add_action('wp_footer', function() {
            ?>
            <script>
            function toggleReadMoreInfo(btn) {
                var parent = btn.closest('.product-additional-information');
                var moreText = parent.querySelector('.more-text-info');
                var previewText = parent.querySelector('.preview-text-info');
                var dots = parent.querySelector('.dots-info');
                
                if (moreText.style.display === "none") {
                    dots.style.display = "none";
                    previewText.style.display = "none";
                    moreText.style.display = "inline";
                    btn.textContent = "Read less";
                } else {
                    dots.style.display = "inline";
                    previewText.style.display = "block";
                    moreText.style.display = "none";
                    btn.textContent = "Read more";
                }
            }
            </script>
            <style>
            .product-additional-information .preview-text-info,
            .product-additional-information .more-text-info {
                display: block;
            }
            .product-additional-information .more-text-info {
                display: none;
            }
            .read-more-btn-info {
                margin-top: 10px;
                cursor: pointer;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                padding: 5px 15px;
                border-radius: 4px;
            }
            .read-more-btn-info:hover {
                background-color: #e0e0e0;
            }
            .dots-info {
                display: inline;
            }
            </style>
            <?php
        }, 99);
    }
    
    return $content;
}
add_filter('woocommerce_product_additional_information', 'filter_additional_information', 10, 1);