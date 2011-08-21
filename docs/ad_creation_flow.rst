
Ad Creation Flow
================

1. The 'classifieds_create_ad' url

   * Redirects authenticated users to the 'classifieds_create_ad_select_category' url
     
   * Shows non-authenticated users a signup / login / pricing template

2. The 'classifieds_create_ad_select_category' url

   * Lists available Category objects as links to the 'classifieds_create_ad_select_category' url

3. The 'classifieds_create_ad_in_category' url

   * Creates an Ad object within the specified Category

   * Redirects to the 'classifieds_create_ad_edit' url

4. The 'classifieds_create_ad_edit' url

   * Retrieves the Ad object

     - Ensures that the ad is not active, because live ads must be edited through the manage views.

     - Ensures that the current user owns the ad

   * Prepares the AdForm and ImageUploadFormSet

   * Renders the appropriate edit template for the category of the ad being edited

   * When submitted, validates the form, resizes uploaded images and generates thumbnails, and redirects to the 'classifieds_create_ad_preview' url.

5. The 'classifieds_create_ad_preview' url

   * Retrieves the ad

     - Ensures that the ad is not active, because live ads must be dealt with through the manage views.

     - Ensures that the current user owns the ad

   * Renders the appropriate preview template for the category that the ad is placed in.

   * Rendered template provides a link to the checkout process

6. Checkout

