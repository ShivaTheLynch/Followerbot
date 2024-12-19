// Remove default additional information tab
add_filter('woocommerce_product_tabs', function($tabs) {
    if (isset($tabs['additional_information'])) {
        unset($tabs['additional_information']);
    }
    
    // Add our custom additional information tab
    $tabs['custom_additional_information'] = array(
        'title'    => __('Additional information', 'woocommerce'),
        'priority' => 20,
        'callback' => 'custom_additional_information_tab'
    );
    
    return $tabs;
}, 98);

// Custom callback for the additional information tab
function custom_additional_information_tab() {
    global $product;
    
    // Get the default additional information content
    ob_start();
    wc_display_product_attributes($product);
    $content = ob_get_clean();
    
    // Create a DOMDocument instance
    $dom = new DOMDocument();
    libxml_use_internal_errors(true);
    
    // Add a root element to ensure proper HTML structure
    $content = '<div>' . $content . '</div>';
    $dom->loadHTML(mb_convert_encoding($content, 'HTML-ENTITIES', 'UTF-8'), LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
    libxml_clear_errors();

    // Find all li elements with class xs-attr
    $xpath = new DOMXPath($dom);
    $items = $xpath->query("//li[contains(@class, 'xs-attr')]");
    
    // If we have more than 5 items
    if ($items->length > 5) {
        // Create a copy of the content for preview
        $previewDom = new DOMDocument();
        $previewDom->loadHTML(mb_convert_encoding($content, 'HTML-ENTITIES', 'UTF-8'), LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
        
        // Get items in preview using xpath
        $previewXpath = new DOMXPath($previewDom);
        $previewItems = $previewXpath->query("//li[contains(@class, 'xs-attr')]");
        
        // Remove items after the 5th one in preview
        for ($i = $previewItems->length - 1; $i >= 5; $i--) {
            $item = $previewItems->item($i);
            $item->parentNode->removeChild($item);
        }

        // Get preview content
        $preview_content = $previewDom->saveHTML();
        
        // Remove the wrapper div we added
        $preview_content = preg_replace('/<\/?div>/', '', $preview_content);
        
        // Output the modified content
        echo '
            <div class="product-additional-info">
                <div class="preview-text">' . $preview_content . '</div>
                <span class="dots">...</span>
                <div class="more-text" style="display: none;">' . $content . '</div>
                <button onclick="toggleReadMore(this)" class="read-more-btn">Read more</button>
            </div>
        ';
    } else {
        // If 5 or fewer items, just output the original content
        echo $content;
    }
}

// Add necessary JavaScript to footer
add_action('wp_footer', function() {
    ?>
    <script>
    function toggleReadMore(btn) {
        var parent = btn.closest('.product-additional-info');
        var moreText = parent.querySelector('.more-text');
        var previewText = parent.querySelector('.preview-text');
        var dots = parent.querySelector('.dots');
        
        if (moreText.style.display === "none") {
            dots.style.display = "none";
            previewText.style.display = "none";
            moreText.style.display = "block";
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
    .product-additional-info .preview-text,
    .product-additional-info .more-text {
        display: block;
    }
    .product-additional-info .more-text {
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
