$(document).ready(function () {
  /*check the aminity */
  let id_ame_list;
  let id_st_list;
  let id_ct_list;
  let ame_list;
  let st_list;
  let addCheck = function() {
    id_ame_list = [];
    id_st_list = [];
    id_ct_list = [];
    ame_list = [];
    st_list = [];
    ct_list = [];
    //get amenities list
    $('div.amenities input[type=checkbox]').each(function () {
      if (this.checked) {
        ame_list.push($(this).attr('data-name'));
        id_ame_list.push($(this).attr('data-id'));
      }
    });
    $('div.amenities > h4').text(ame_list.join(', '));
    //get state list
    $('div.locations h2 input[type=checkbox]').each(function () {
      if (this.checked) {
        st_list.push($(this).attr('data-name'));
        id_st_list.push($(this).attr('data-id'));
      }
    });
    $('div.locations > h4').text(st_list.join(', '));
    //get city list
    $('div.locations li input[type=checkbox]').each(function () {
      if (this.checked) {
        st_list.push($(this).attr('data-name'));
        id_ct_list.push($(this).attr('data-id'));
      }
    });
    $('div.locations > h4').text(st_list.join(', '));
  }
  $('input[type=checkbox]').on('click', addCheck);
  /* update status */
  let url = 'http://0.0.0.0:5001/api/v1/status/';
  $.get(url, function(status) {
    if (status.status === 'OK') {
      $('#api_status').addClass('available');
    } else {
      $('#api_status').removeClass('available');
    }
  });
  /* search place handling */
  function get_place(dict) {
    $.ajax({
      url: 'http://0.0.0.0:5001/api/v1/places_search/',
      dataType: 'json',
      type: 'post',
      contentType: 'application/json',
      data: JSON.stringify(dict),
      success: function( data, textStatus, jQxhr ){
      	data.sort(function (a, b) {
          let keyA = a.name.toUpperCase();
          let keyB = b.name.toUpperCase();
          if(keyA < keyB) return -1;
          if(keyA > keyB) return 1;
          return 0;
        });
        for (let i in data) {
          let d = data[i];
          let user_url = 'http://0.0.0.0:5001/api/v1/users/' + d.user_id;
          let review_url = 'http://0.0.0.0:5001/api/v1/places/' + d.id + '/reviews';
          let ame_url = 'http://0.0.0.0:5001/api/v1/places/' + d.id + '/amenities';
          $.when($.ajax(user_url), $.ajax(review_url), $.ajax(ame_url)).done(function(user_d, review_d, ame_d) {
            let user = user_d[0].first_name + ' ' + user_d[0].last_name;
            let amenities_list = "";
            for (let j in ame_d[0]) {
              amenities_list += '<div class="' + ame_d[0][j].name + '">' + ame_d[0][j].name + '</div>';
            }
            let review_arr = [];
            review_d[0].forEach(rev => {
              review_arr.push(new Promise((resolve, reject) => {
                let review_name = ' on ' + rev.updated_at + '</h3>';
                let review_user_id_url = 'http://0.0.0.0:5001/api/v1/users/' + rev.user_id;
                $.get(review_user_id_url, function(data) {
                  review_name = '<h3 style="font-size: 14px;">From ' + data.first_name + ' ' + data.last_name + review_name;
                  resolve(review_name + '<p>' + rev.text + '</p>');
                });
              }))
            });
            Promise.all(review_arr).then(list => {
              let review_list = list.join('');
                  $('section.places').append(
      	      '<article>' +
      		  '<div class="title"><h2>' + d.name + '</h2>' +
      		  '<div class="price_by_night">' + d.price_by_night + '</div>' +
      		  '</div>' +
      		  '<div class="information">' +
                          '<div class="max_guest">' +
                            '<i class="fa fa-users fa-3x" aria-hidden="true"></i>' +
                            '<br />' + d.max_guest + 'Guests' +
                          '</div>' +
                          '<div class="number_rooms">' +
                            '<i class="fa fa-bed fa-3x" aria-hidden="true"></i>' +
                            '<br />' + d.number_rooms + 'Bedrooms' +
                          '</div>' +
                          '<div class="number_bathrooms">' +
                            '<i class="fa fa-bath fa-3x" aria-hidden="true"></i>' +
                            '<br />' + d.number_bathrooms + 'Bathroom' +
                          '</div>' +
      		  '</div>' +
      		  '<div class="user"><strong>Owner: ' + user + '</strong></div>' +
      		  '<div class="description">' + d.description + '</div>' +
      		  '<div class="amenities"><h2 style="font-size:16px; border-bottom:1px solid #DDDDDD; text-align:left;">Amenities</h2></div>' +
                          '<ul>' + amenities_list + '</ul>' +
      		  '<div class="reviews"><h2 style="font-size:16px; border-bottom:1px solid #DDDDDD; text-align:left;">Reviews</h2>' +
            '<a class="review_post" href="/review_post/' + d.id + '">Click for review this post</a>' +
                          '<ul>' +
                            review_list +
                          '</ul>' +
      		  '</div>' +
      	      '</article>');
            });
          });
        }
      },
      error: function( jqXhr, textStatus, errorThrown ){
          console.log( errorThrown );
      }
    });
  }

  $('button.Search').click(function () {
    let dic = {'states': [], 'cities': [], 'amenities': []};
    for (let i in id_ame_list) {
      dic['amenities'].push(String(id_ame_list[i]));
    }
    for (let i in id_st_list) {
      dic['states'].push(String(id_st_list[i]));
    }
    for (let i in id_ct_list) {
      dic['cities'].push(String(id_ct_list[i]));
    }
    $('article').remove();
    get_place(dic, ame_list);
    ame_list = [];
    st_list = [];
    ct_list = [];
  });

  // get_place({});
});
