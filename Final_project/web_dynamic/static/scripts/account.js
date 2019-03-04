$(document).ready(function () {
  /* search place handling */
  function get_place(id, name) {
    $.ajax({
      url: 'http://0.0.0.0:5001/api/v1/users/' + id + '/places',
      dataType: 'json',
      type: 'get',
      contentType: 'application/json',
      data: JSON.stringify({}),
      success: function( data, textStatus, jQxhr ){
        for (let i in data) {
          let d = data[i];
          let review_url = 'http://0.0.0.0:5001/api/v1/places/' + d.id + '/reviews';
          let ame_url = 'http://0.0.0.0:5001/api/v1/places/' + d.id + '/amenities';
          $.when($.ajax(review_url), $.ajax(ame_url)).done(function(review_d, ame_d) {
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
              // let string = 'http://0.0.0.0:5001/update_post';
              // console.log(string);
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
      		  '<div class="user"><strong>Owner: ' + name + '</strong></div>' +
      		  '<div class="description">' + d.description + '</div>' +
      		  '<div class="amenities"><h2 style="font-size:16px; border-bottom:1px solid #DDDDDD; text-align:left;">Amenities</h2></div>' +
                          '<ul>' + amenities_list + '</ul>' +
      		  '<div class="reviews"><h2 style="font-size:16px; border-bottom:1px solid #DDDDDD; text-align:left;">Reviews</h2>' +
                          '<ul>' +
                            review_list +
                          '</ul>' +
      		  '</div>' +
            '<a class="update_post" href="/update_post/' + d.id + '">Click for update this post</a>' +
            '<a class="update_post" href="/delete_post/' + d.id + '">Click for delete this post</a>' +
      	      '</article>');
            });
          });
        }
      }
    });
  }
  let id = $('div.current_user').text()
  let name = $('div.current_user_name').text()
  get_place(id, name);
});
