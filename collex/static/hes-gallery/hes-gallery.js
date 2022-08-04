var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/*!

	HesGallery v1.5.1

	Copyright (c) 2018-2019 Artur Medrygal <medrygal.artur@gmail.com>

	Product under MIT licence

*/

var HesGallery = {
  version: '1.5.1',
  options: {
    // Global
    disableScrolling: false,
    hostedStyles: true,
    animations: true,
    keyboardControl: true,
    minResolution: 0,
    autoInit: true,

    // Local
    wrapAround: false,
    showImageCount: true,

    // set to true if images are nested in links
    linkNested: false
  },

  setOptions: function setOptions() {
    var values = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

    for (var key in values) {
      this.options[key] = values[key];
    }
  },
  init: function init(options) {
    var _this = this;

    this.setOptions(options);

    if (!this.executed) this.createDOM();

    if (this.options.animations) this.elements.pic_cont.classList = 'hg-transition';else this.elements.pic_cont.classList = '';

    this.count = document.querySelectorAll('.hes-gallery').length;

    this.galleries = [];

    for (var i = 0; i < this.count; i++) {
      // Creates a galleries
      this.galleries[i] = new this.HesSingleGallery(i, this);
    }

    // KeyDown event listener
    if (this.options.keyboardControl && !this.keydownEventListener) {
      addEventListener('keydown', function (_ref) {
        var keyCode = _ref.keyCode;

        if (keyCode == 39 && _this.open && _this.options.keyboardControl) _this.next();
        if (keyCode == 37 && _this.open && _this.options.keyboardControl) _this.prev();
        if (keyCode == 27 && _this.open && _this.options.keyboardControl) _this.hide();
      });
      this.keydownEventListener = true;
    }

    return 'HesGallery initiated!';
  },
  replaceImages: function replaceImages(gallery) {
    gallery.querySelectorAll('a.hg-image').forEach(function (imageLink) {
      image = imageLink.getElementsByTagName('img')[0];
      image.setAttribute('data-fullsize', imageLink.href.trim());
      imageLink.replaceWith(image);
    });
  },
  createDOM: function createDOM() {
    var _this2 = this;

    // Creates DOM Elements for gallery
    this.elements = {};

    if (this.options.hostedStyles) document.head.innerHTML += "<link rel='stylesheet' href='https://unpkg.com/hes-gallery/dist/hes-gallery.min.css'>";

    var gallery = document.createElement('div');
    gallery.id = 'hgallery';
    gallery.setAttribute('style', 'visibility:hidden;');

    this.elements.gallery = gallery; // Whole gallery

    this.elements.gallery.innerHTML += '\n      ' +
        '<div id=\'hg-bg\'></div>\n      ' +
        '<div id=\'hg-pic-cont\'>\n        ' +
            '<img id=\'hg-pic\' />\n        ' +
            '<div id=\'hg-prev-onpic\'></div>\n        ' +
            '<div id=\'hg-next-onpic\'></div>\n        ' +
            '<div id=\'hg-subtext\'></div>\n        ' +
            '<div id=\'hg-howmany\'></div>\n      ' +
        '</div>\n      ' +
        '<div id=\'hg-colors\'></div>' +
        '<button id=\'hg-prev\' title="Previous" aria-label="Next">\n        ' +
            '<img src="data:image/svg+xml;base64,PHN2ZyBmaWxsPSIjZmZmZmZmIiBoZWlnaHQ9IjI0IiB2aWV3Qm94PSIwIDAgMjQgMjQiIHdpZHRoPSIyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCiAgICA8cGF0aCBkPSJNOC41OSAxNi4zNGw0LjU4LTQuNTktNC41OC00LjU5TDEwIDUuNzVsNiA2LTYgNnoiLz4NCiAgICA8cGF0aCBkPSJNMC0uMjVoMjR2MjRIMHoiIGZpbGw9Im5vbmUiLz4NCjwvc3ZnPg==" alt="Previous" />\n      ' +
        '</button>\n      ' +
        '<button id=\'hg-next\' title="Next" aria-label="Previous">\n        ' +
            '<img src="data:image/svg+xml;base64,PHN2ZyBmaWxsPSIjZmZmZmZmIiBoZWlnaHQ9IjI0IiB2aWV3Qm94PSIwIDAgMjQgMjQiIHdpZHRoPSIyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCiAgICA8cGF0aCBkPSJNOC41OSAxNi4zNGw0LjU4LTQuNTktNC41OC00LjU5TDEwIDUuNzVsNiA2LTYgNnoiLz4NCiAgICA8cGF0aCBkPSJNMC0uMjVoMjR2MjRIMHoiIGZpbGw9Im5vbmUiLz4NCjwvc3ZnPg==" alt="Next" />\n      ' +
        '</button>\n    ';

    document.body.appendChild(gallery);

    this.elements.colors = document.getElementById('hg-colors');

    this.elements.b_prev = document.getElementById('hg-prev');
    this.elements.b_next = document.getElementById('hg-next');

    this.elements.pic_cont = document.getElementById('hg-pic-cont');

    this.elements.b_next_onpic = document.getElementById('hg-next-onpic');
    this.elements.b_prev_onpic = document.getElementById('hg-prev-onpic');

    this.elements.b_prev.onclick = this.elements.b_prev_onpic.onclick = function () {
      _this2.prev();
    };

    this.elements.b_next.onclick = this.elements.b_next_onpic.onclick = function () {
      _this2.next();
    };

    document.getElementById('hg-bg').onclick = function () {
      _this2.hide();
    };

    this.executed = true;
  },
  show: function show(g, i) {
    if (innerWidth < this.options.minResolution) return false; // If browser width is less than min resolution in settings

    this.currentImg = i;
    this.currentGal = g;

    this.open = true;

    if (this.options.animations || this.elements.pic_cont.classList == 'hg-transition') this.elements.pic_cont.classList.remove('hg-transition');

    document.getElementById('hg-pic').setAttribute('src', this.galleries[g].imgPaths[i]); // Sets the path to image

    document.getElementById('hg-pic').alt = this.galleries[g].altTexts[i]; // Sets alt attribute

    this.elements.gallery.classList.add('open');

    document.getElementById('hg-subtext').innerHTML = this.galleries[g].subTexts[i];

    if (this.galleries[this.currentGal].options.showOsLink)
      document.getElementById('hg-howmany').innerHTML = `<a href="https://opensea.io/assets/${this.galleries[this.currentGal].contractAddress}/${this.galleries[g].tokenIds[i]}" target="_blank">View on OpenSea</a>`;
    else if (this.galleries[this.currentGal].options.showImageCount && this.galleries[this.currentGal].imgPaths.length != 1)
      document.getElementById('hg-howmany').innerHTML = this.currentImg + 1 + '/' + this.galleries[g].count;
    else document.getElementById('hg-howmany').innerHTML = '';

    this.elements.colors.innerHTML = '';


    // Visibility of next/before buttons in gallery
    if (this.galleries[this.currentGal].imgPaths.length == 1) {
      // One image in gallery
      this.elements.b_prev.classList = 'hg-unvisible';
      this.elements.b_prev_onpic.classList = 'hg-unvisible';
      this.elements.b_next.classList = 'hg-unvisible';
      this.elements.b_next_onpic.classList = 'hg-unvisible';
    } else if (this.currentImg + 1 == 1 && !this.galleries[this.currentGal].options.wrapAround) {
      // First photo
      this.elements.b_prev.classList = 'hg-unvisible';
      this.elements.b_prev_onpic.classList = 'hg-unvisible';

      this.elements.b_next.classList = '';
      this.elements.b_next_onpic.classList = '';
    } else if (this.currentImg + 1 == this.galleries[this.currentGal].count && !this.galleries[this.currentGal].options.wrapAround) {
      // Last photo
      this.elements.b_next.classList = 'hg-unvisible';
      this.elements.b_next_onpic.classList = 'hg-unvisible';

      this.elements.b_prev.classList = '';
      this.elements.b_prev_onpic.classList = '';
    } else {
      // Any other photo
      this.elements.b_next.classList = '';
      this.elements.b_next_onpic.classList = '';

      this.elements.b_prev.classList = '';
      this.elements.b_prev_onpic.classList = '';
    }

    if (this.options.disableScrolling) document.body.classList += ' hg-disable-scrolling'; // Disable scroll
  },
  hide: function hide() {
    if (this.options.animations) this.elements.pic_cont.classList.add('hg-transition');

    this.elements.gallery.classList.remove('open');
    this.open = false;
    if (this.options.disableScrolling) document.body.classList.remove('hg-disable-scrolling'); // Enable scroll

    removeHash();
  },
  next: function next() {
    if (this.galleries[this.currentGal].options.wrapAround && this.currentImg == this.galleries[this.currentGal].count - 1) this.show(this.currentGal, 0);else if (this.currentImg + 1 < this.galleries[this.currentGal].count) this.show(this.currentGal, this.currentImg + 1);
  },
  prev: function prev() {
    if (this.galleries[this.currentGal].options.wrapAround && this.currentImg == 0) this.show(this.currentGal, this.galleries[this.currentGal].count - 1);else if (this.currentImg + 1 > 1) this.show(this.currentGal, this.currentImg - 1);
  },


  HesSingleGallery: function HesSingleGallery(index, root) {
    var _this3 = this;

    _classCallCheck(this, HesSingleGallery);

    this.root = root;
    this.index = index;
    this.imgPaths = [];
    this.subTexts = [];
    this.tokenIds = [];
    this.altTexts = [];

    this.options = {};

    var gallery = document.getElementsByClassName('hes-gallery')[this.index];
    this.contractAddress = gallery.dataset.contract_address;

    if (this.root.options.linkNested) this.root.replaceImages(gallery);

    this.options.wrapAround = gallery.hasAttribute('data-wrap') ? gallery.dataset.wrap == 'true' : this.root.options.wrapAround;
    this.options.showImageCount = gallery.hasAttribute('data-img-count') ? gallery.dataset.imgCount == 'true' : this.root.options.showImageCount;
    this.options.showOsLink = gallery.hasAttribute('data-os-link') ? gallery.dataset.os_link == 'true' : this.root.options.showOsLink;

    var disabledCount = 0;
    gallery.querySelectorAll('img').forEach(function (image, i) {
      if (image.hasAttribute('data-disabled')) disabledCount++;else {
        var imagePath = image.dataset.fullsize || image.dataset.src || image.src;
        if (imagePath) _this3.imgPaths.push(imagePath);
        _this3.subTexts.push(image.dataset.subtext || '');
        _this3.tokenIds.push(image.dataset.token_id || '');
        _this3.altTexts.push(image.alt || '');

        image.onclick = function () {
          _this3.root.show(_this3.index, i - disabledCount);
        };
      }
    });

    this.count = this.imgPaths.length;
  }
};

document.addEventListener('DOMContentLoaded', function () {
  if (HesGallery.options.autoInit) HesGallery.init();
});

if ('object' == (typeof exports === 'undefined' ? 'undefined' : _typeof(exports)) && 'undefined' != typeof module) module.exports = HesGallery;

// NodeList polyfill
if (typeof NodeList !== 'undefined' && NodeList.prototype && !NodeList.prototype.forEach) {
  NodeList.prototype.forEach = Array.prototype.forEach;
}

function removeHash () {
    var scrollV, scrollH, loc = window.location;
    if ("pushState" in history)
        history.pushState("", document.title, loc.pathname + loc.search);
    else {
        // Prevent scrolling by storing the page's current scroll offset
        scrollV = document.body.scrollTop;
        scrollH = document.body.scrollLeft;

        loc.hash = "";

        // Restore the scroll offset, should be flicker free
        document.body.scrollTop = scrollV;
        document.body.scrollLeft = scrollH;
    }
}